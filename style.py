import ttkbootstrap as ttk

def appliquer_theme(root, theme="superhero"):
    """
    Applique un thème global à l'application.
    Les thèmes disponibles : darkly, flatly, journal, superhero, etc.
    """
    style = ttk.Style()
    style.theme_use(theme)
    return style


def styliser_bouton(widget, couleur="primary"):
    """Applique un style Bootstrap à un bouton."""
    widget.configure(bootstyle=couleur)


def styliser_label(widget):
    """Applique un style aux labels."""
    widget.configure(font=("Arial", 12), bootstyle="inverse-light")


def styliser_entry(widget):
    """Applique un style aux champs de saisie."""
    widget.configure(font=("Arial", 12), bootstyle="light")


def styliser_frame(widget):
    """Applique un style aux cadres."""
    widget.configure(bootstyle="info")


def styliser_treeview(widget):
    """Applique un style au tableau Treeview."""
    widget.configure(bootstyle="light")

