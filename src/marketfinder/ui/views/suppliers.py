"""CRUD mínimo de proveedores."""

from __future__ import annotations

import customtkinter as ctk

from marketfinder.config import theme
from marketfinder.core.models import Supplier
from marketfinder.data.repositories import OfferRepository, SupplierRepository
from marketfinder.ui.views.base import ScrollableView


class SuppliersView(ScrollableView):
    def __init__(self, master, *, conn, **kwargs) -> None:
        super().__init__(master, title="Proveedores", **kwargs)
        self.conn = conn
        self.repo = SupplierRepository(conn)
        self.offers = OfferRepository(conn)
        self._edit_id: int | None = None
        self._build()
        self.refresh()

    def _build(self) -> None:
        form = ctk.CTkFrame(
            self.body, fg_color=theme.PANEL, corner_radius=10, border_width=1, border_color=theme.BORDER
        )
        form.grid(row=0, column=0, sticky="ew", padx=12, pady=8)
        form.grid_columnconfigure((1, 3), weight=1)

        ctk.CTkLabel(form, text="Preferente México (MX) — editable", text_color=theme.PRIMARY).grid(
            row=0, column=0, columnspan=4, padx=12, pady=(10, 4), sticky="w"
        )

        self.name_var = ctk.StringVar()
        self.country_var = ctk.StringVar(value="MX")
        self.contact_var = ctk.StringVar()
        self.url_var = ctk.StringVar()
        self.lead_var = ctk.StringVar()
        self.notes_var = ctk.StringVar()

        self._field(form, 1, 0, "Nombre*", self.name_var)
        self._field(form, 1, 2, "País", self.country_var)
        self._field(form, 2, 0, "Contacto", self.contact_var)
        self._field(form, 2, 2, "URL", self.url_var)
        self._field(form, 3, 0, "Lead days", self.lead_var)
        self._field(form, 3, 2, "Notas", self.notes_var)

        btns = ctk.CTkFrame(form, fg_color="transparent")
        btns.grid(row=4, column=0, columnspan=4, padx=12, pady=10, sticky="w")
        ctk.CTkButton(
            btns, text="Guardar", fg_color=theme.PRIMARY, text_color=theme.BG, command=self._save
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(btns, text="Limpiar", fg_color=theme.BORDER, command=self._clear).pack(side="left")

        self.status = ctk.CTkLabel(form, text="", text_color=theme.TEXT_MUTED)
        self.status.grid(row=5, column=0, columnspan=4, padx=12, pady=(0, 10), sticky="w")

        self.list_frame = ctk.CTkFrame(self.body, fg_color="transparent")
        self.list_frame.grid(row=1, column=0, sticky="ew", padx=12, pady=8)
        self.list_frame.grid_columnconfigure(0, weight=1)

    def _field(self, parent, row, col, label, var):
        ctk.CTkLabel(parent, text=label, text_color=theme.TEXT_MUTED).grid(
            row=row, column=col, padx=12, pady=4, sticky="w"
        )
        ctk.CTkEntry(parent, textvariable=var).grid(
            row=row, column=col + 1, padx=8, pady=4, sticky="ew"
        )

    def refresh(self) -> None:
        for w in self.list_frame.winfo_children():
            w.destroy()
        items = self.repo.list_all()
        if not items:
            ctk.CTkLabel(
                self.list_frame, text="Sin proveedores registrados.", text_color=theme.TEXT_MUTED
            ).grid(row=0, column=0, sticky="w")
            return
        for i, s in enumerate(items):
            n_offers = len(self.offers.list_for_supplier(s.id))  # type: ignore[arg-type]
            row = ctk.CTkFrame(
                self.list_frame, fg_color=theme.PANEL, corner_radius=8, border_width=1, border_color=theme.BORDER
            )
            row.grid(row=i, column=0, sticky="ew", pady=4)
            row.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(
                row,
                text=f"#{s.id}  {s.name}  ·  {s.country}  ·  ofertas: {n_offers}",
                text_color=theme.TEXT,
                anchor="w",
                wraplength=480,
                justify="left",
            ).grid(row=0, column=0, padx=12, pady=10, sticky="ew")
            ctk.CTkButton(
                row, text="Editar", width=70, fg_color=theme.BORDER, command=lambda x=s: self._load(x)
            ).grid(row=0, column=1, padx=4, pady=8)
            ctk.CTkButton(
                row,
                text="Borrar",
                width=70,
                fg_color=theme.ERROR,
                command=lambda sid=s.id: self._delete(sid),
            ).grid(row=0, column=2, padx=(4, 12), pady=8)

    def _load(self, s: Supplier) -> None:
        self._edit_id = s.id
        self.name_var.set(s.name)
        self.country_var.set(s.country)
        self.contact_var.set(s.contact or "")
        self.url_var.set(s.url or "")
        self.lead_var.set("" if s.default_lead_days is None else str(s.default_lead_days))
        self.notes_var.set(s.notes or "")
        self.status.configure(text=f"Editando #{s.id}")

    def _clear(self) -> None:
        self._edit_id = None
        self.name_var.set("")
        self.country_var.set("MX")
        self.contact_var.set("")
        self.url_var.set("")
        self.lead_var.set("")
        self.notes_var.set("")
        self.status.configure(text="")

    def _save(self) -> None:
        name = self.name_var.get().strip()
        if not name:
            self.status.configure(text="Nombre obligatorio", text_color=theme.ERROR)
            return
        lead_raw = self.lead_var.get().strip()
        lead = int(lead_raw) if lead_raw else None
        s = Supplier(
            id=self._edit_id,
            name=name,
            country=self.country_var.get().strip() or "MX",
            contact=self.contact_var.get().strip() or None,
            url=self.url_var.get().strip() or None,
            default_lead_days=lead,
            notes=self.notes_var.get().strip() or None,
        )
        if self._edit_id:
            self.repo.update(s)
        else:
            self.repo.create(s)
        self.status.configure(text="Guardado", text_color=theme.PRIMARY)
        self._clear()
        self.refresh()

    def _delete(self, supplier_id: int | None) -> None:
        if supplier_id is None:
            return
        self.repo.delete(supplier_id)
        self.refresh()
