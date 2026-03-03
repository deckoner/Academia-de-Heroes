from django import forms
from app.models import Personaje


class PersonajeForm(forms.ModelForm):
    """
    Formulario basado en el modelo Personaje para la creación y edición de personajes.

    Proporciona una interfaz de usuario validada para los campos del modelo,
    incluyendo la selección del tipo de personaje y sus atributos específicos.

    Attributes
    ----------
    tipo : forms.ChoiceField
        Campo de selección para el tipo de personaje (Guerrero, Mago, Arquero).
    """

    TIPO_CHOICES = [
        ("", "Selecciona un tipo"),
        ("GUERRERO", "Guerrero"),
        ("MAGO", "Mago"),
        ("ARQUERO", "Arquero"),
    ]

    tipo = forms.ChoiceField(
        choices=TIPO_CHOICES,
        required=True,
        label="Tipo de Personaje",
        widget=forms.Select(attrs={"class": "form-control", "id": "id_tipo"}),
    )

    nombre = forms.CharField(
        max_length=100,
        required=True,
        label="Nombre",
        help_text="Nombre único del personaje",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Introduce el nombre del personaje",
                "id": "id_nombre",
            }
        ),
    )

    nivel = forms.IntegerField(
        initial=1,
        min_value=1,
        max_value=100,
        required=True,
        label="Nivel",
        help_text="Nivel del personaje (1-100)",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "min": "1", "max": "100", "id": "id_nivel"}
        ),
    )

    vida = forms.IntegerField(
        min_value=0,
        required=True,
        label="Puntos de Vida",
        help_text="Vida actual del personaje",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "min": "0", "id": "id_vida"}
        ),
    )

    vida_max = forms.IntegerField(
        min_value=1,
        required=True,
        label="Vida Máxima",
        help_text="Vida máxima del personaje",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "min": "1", "id": "id_vida_max"}
        ),
    )

    armadura = forms.IntegerField(
        initial=5,
        min_value=0,
        required=False,
        label="Armadura",
        help_text="Puntos de armadura (solo para Guerreros)",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "min": "0", "id": "id_armadura"}
        ),
    )

    mana = forms.IntegerField(
        initial=50,
        min_value=0,
        required=False,
        label="Mana",
        help_text="Puntos de mana (solo para Magos)",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "min": "0", "id": "id_mana"}
        ),
    )

    precision = forms.IntegerField(
        initial=80,
        min_value=0,
        max_value=100,
        required=False,
        label="Precisión",
        help_text="Porcentaje de precisión (solo para Arqueros)",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "min": "0",
                "max": "100",
                "id": "id_precision",
            }
        ),
    )

    class Meta:
        """
        Metadatos del formulario que definen el modelo y campos asociados.
        """

        model = Personaje
        fields = ["tipo", "nombre", "nivel", "vida", "vida_max"]

    def clean(self):
        """
        Valida los datos del formulario asegurando que los campos específicos
        de cada tipo de personaje estén presentes.

        Returns
        -------
        dict
            Datos cleaned_data si son válidos.

        Raises
        ------
        forms.ValidationError
            Si los campos específicos no coinciden con el tipo de personaje.
        """
        cleaned_data = super().clean()
        tipo = cleaned_data.get("tipo")

        if tipo == "GUERRERO" and not cleaned_data.get("armadura"):
            cleaned_data["armadura"] = 5

        if tipo == "MAGO" and not cleaned_data.get("mana"):
            cleaned_data["mana"] = 50

        if tipo == "ARQUERO" and not cleaned_data.get("precision"):
            cleaned_data["precision"] = 80

        precision = cleaned_data.get("precision")
        if precision is not None:
            if precision < 0 or precision > 100:
                raise forms.ValidationError(
                    {"precision": "La precisión debe estar entre 0 y 100."}
                )

        return cleaned_data

    def save(self, commit=True):
        """
        Guarda el personaje en la base de datos.

        Parameters
        ----------
        commit : bool
            Si True, guarda el objeto en la base de datos.

        Returns
        -------
        Personaje
            Instancia del personaje guardado.
        """
        personaje = super().save(commit=False)

        tipo = self.cleaned_data.get("tipo")
        personaje.tipo = tipo

        if tipo == "GUERRERO":
            personaje.armadura = self.cleaned_data.get("armadura", 5)
        elif tipo == "MAGO":
            personaje.mana = self.cleaned_data.get("mana", 50)
        elif tipo == "ARQUERO":
            personaje.precision = self.cleaned_data.get("precision", 80)

        if commit:
            personaje.save()

        return personaje
