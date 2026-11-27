"""CRUD mínimo de productos + ofertas."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

import customtkinter as ctk

from marketfinder.config import theme
from marketfinder.core.models import Offer, OfferKind, Product, Provenance
from marketfinder.data.repositories import (
    OfferRepository,
    ProductRepository,
    SupplierRepository,
)
from marketfinder.ui.views.base import ScrollableView


class ProductsView(ScrollableView):
    def __init__(self, master, *, conn, **kwargs) -> None:
        super().__init__(master, title="Productos", **kwargs)
        self.conn = conn
        self.products = ProductRepository(conn)
        self.suppliers = SupplierRepository(conn)
        self.offers = OfferRepository(conn)
        self._build_form()
        self._build_list()
        self.refresh()

    def _build_form(self) -> None:
        form = ctk.CTkFrame(
            self.body, fg_color=theme.PANEL, corner_radius=10, border_width=1, border_color=theme.BORDER
        )
        form.grid(row=0, column=0, sticky="ew", padx=12, pady=8)
        form.grid_columnconfigure((1, 3), weight=1)

        ctk.CTkLabel(form, text="Nuevo / editar producto", text_color=theme.PRIMARY).grid(
            row=0, column=0, columnspan=4, padx=12, pady=(10, 4), sticky="w"
        )

        self.name_var = ctk.StringVar()
        self.sku_var = ctk.StringVar()
        self.category_var = ctk.StringVar()
        self.weight_var = ctk.StringVar()
        self.notes_var = ctk.StringVar()
        self._edit_id: int | None = None

        self._labeled_entry(form, 1, 0, "Nombre*", self.name_var)
        self._labeled_entry(form, 1, 2, "SKU", self.sku_var)
        self._labeled_entry(form, 2, 0, "Categoría", self.category_var)
        self._labeled_entry(form, 2, 2, "Peso (g)", self.weight_var)
        self._labeled_entry(form, 3, 0, "Notas", self.notes_var, colspan=3)

        # Oferta vinculada
        ctk.CTkLabel(form, text="Oferta (proveedor)", text_color=theme.TEXT_MUTED).grid(
            row=4, column=0, padx=12, pady=(8, 0), sticky="w"
        )
        self.supplier_menu = ctk.CTkOptionMenu(form, values=["— sin proveedor —"])
        self.supplier_menu.grid(row=4, column=1, padx=8, pady=(8, 0), sticky="ew")
        self.cost_var = ctk.StringVar()
        self._labeled_entry(form, 4, 2, "Costo unitario", self.cost_var)
        self.prov_menu = ctk.CTkOptionMenu(
            form, values=[p.value for p in Provenance]
        )
        self.prov_menu.set(Provenance.PENDIENTE.value)
        ctk.CTkLabel(form, text="Proveniencia costo", text_color=theme.TEXT_MUTED).grid(
            row=5, column=0, padx=12, pady=4, sticky="w"
        )
        self.prov_menu.grid(row=5, column=1, padx=8, pady=4, sticky="ew")

        btns = ctk.CTkFrame(form, fg_color="transparent")
        btns.grid(row=6, column=0, columnspan=4, padx=12, pady=10, sticky="w")
        ctk.CTkButton(
            btns, text="Guardar", fg_color=theme.PRIMARY, text_color=theme.BG, command=self._save
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            btns, text="Limpiar", fg_color=theme.BORDER, command=self._clear
        ).pack(side="left")

        self.status = ctk.CTkLabel(form, text="", text_color=theme.TEXT_MUTED)
        self.status.grid(row=7, column=0, columnspan=4, padx=12, pady=(0, 10), sticky="w")

    def _labeled_entry(self, parent, row, col, label, var, colspan=1):
        ctk.CTkLabel(parent, text=label, text_color=theme.TEXT_MUTED).grid(
            row=row, column=col, padx=12, pady=4, sticky="w"
        )
        ctk.CTkEntry(parent, textvariable=var).grid(
            row=row, column=col + 1, columnspan=colspan, padx=8, pady=4, sticky="ew"
        )

    def _build_list(self) -> None:
        self.list_frame = ctk.CTkFrame(self.body, fg_color="transparent")
        self.list_frame.grid(row=1, column=0, sticky="ew", padx=12, pady=8)
        self.list_frame.grid_columnconfigure(0, weight=1)

    def refresh(self) -> None:
        suppliers = self.suppliers.list_all()
        labels = ["— sin proveedor —"] + [f"{s.id}: {s.name}" for s in suppliers]
        self.supplier_menu.configure(values=labels)
        self.supplier_menu.set(labels[0])

        for w in self.list_frame.winfo_children():
            w.destroy()

        products = self.products.list_all()
        if not products:
            ctk.CTkLabel(
                self.list_frame,
                text="Sin productos. Los datos de prueba deben etiquetarse como ficticios.",
                text_color=theme.TEXT_MUTED,
            ).grid(row=0, column=0, sticky="w")
            return

        for i, p in enumerate(products):
            offers = self.offers.list_for_product(p.id)  # type: ignore[arg-type]
            offer_txt = (
                ", ".join(
                    f"prov#{o.supplier_id} ${o.unit_cost} [{o.unit_cost_provenance}]"
                    if o.unit_cost is not None
                    else f"prov#{o.supplier_id} (costo pendiente)"
                    for o in offers
                )
                or "sin ofertas"
            )
            row = ctk.CTkFrame(
                self.list_frame, fg_color=theme.PANEL, corner_radius=8, border_width=1, border_color=theme.BORDER
            )
            row.grid(row=i, column=0, sticky="ew", pady=4)
            row.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(
                row,
                text=f"#{p.id}  {p.name}  ·  {p.sku or 's/SKU'}  ·  {offer_txt}",
                text_color=theme.TEXT,
                anchor="w",
            ).grid(row=0, column=0, padx=12, pady=10, sticky="ew")
            ctk.CTkButton(
                row, text="Editar", width=70, fg_color=theme.BORDER, command=lambda prod=p: self._load(prod)
            ).grid(row=0, column=1, padx=4, pady=8)
            ctk.CTkButton(
                row,
                text="Borrar",
                width=70,
                fg_color=theme.ERROR,
                command=lambda pid=p.id: self._delete(pid),
            ).grid(row=0, column=2, padx=(4, 12), pady=8)

    def _load(self, product: Product) -> None:
        self._edit_id = product.id
        self.name_var.set(product.name)
        self.sku_var.set(product.sku or "")
        self.category_var.set(product.category or "")
        self.weight_var.set(str(product.weight_grams) if product.weight_grams is not None else "")
        self.notes_var.set(product.notes or "")
        self.status.configure(text=f"Editando #{product.id}")

    def _clear(self) -> None:
        self._edit_id = None
        self.name_var.set("")
        self.sku_var.set("")
        self.category_var.set("")
        self.weight_var.set("")
        self.notes_var.set("")
        self.cost_var.set("")
        self.prov_menu.set(Provenance.PENDIENTE.value)
        self.status.configure(text="")

    def _parse_weight(self) -> Decimal | None:
        raw = self.weight_var.get().strip()
        if not raw:
            return None
        try:
            return Decimal(raw)
        except InvalidOperation:
            raise ValueError("Peso inválido")

    def _parse_cost(self) -> Decimal | None:
        raw = self.cost_var.get().strip()
        if not raw:
            return None
        try:
            return Decimal(raw)
        except InvalidOperation:
            raise ValueError("Costo inválido")

    def _save(self) -> None:
        name = self.name_var.get().strip()
        if not name:
            self.status.configure(text="Nombre obligatorio", text_color=theme.ERROR)
            return
        try:
            weight = self._parse_weight()
            cost = self._parse_cost()
        except ValueError as exc:
            self.status.configure(text=str(exc), text_color=theme.ERROR)
            return

        product = Product(
            id=self._edit_id,
            name=name,
            sku=self.sku_var.get().strip() or None,
            category=self.category_var.get().strip() or None,
            weight_grams=weight,
            notes=self.notes_var.get().strip() or None,
            kind=OfferKind.UNITARIO,
        )
        if self._edit_id:
            self.products.update(product)
        else:
            self.products.create(product)

        supplier_label = self.supplier_menu.get()
        if supplier_label != "— sin proveedor —" and product.id is not None:
            sid = int(supplier_label.split(":", 1)[0])
            existing = [
                o for o in self.offers.list_for_product(product.id) if o.supplier_id == sid
            ]
            offer = Offer(
                id=existing[0].id if existing else None,
                product_id=product.id,
                supplier_id=sid,
                unit_cost=cost,
                unit_cost_provenance=Provenance(self.prov_menu.get()),
            )
            if existing:
                self.offers.update(offer)
            else:
                self.offers.create(offer)

        self.status.configure(text="Guardado", text_color=theme.PRIMARY)
        self._clear()
        self.refresh()

    def _delete(self, product_id: int | None) -> None:
        if product_id is None:
            return
        self.products.delete(product_id)
        self.refresh()
