import pytest
from django.test import TestCase
from app.forms import PersonajeForm


@pytest.mark.unit
class TestPersonajeForm(TestCase):
    """Tests para el formulario PersonajeForm."""
    
    def test_form_valido_guerrero(self):
        """Verifica que el formulario es valido con datos de guerrero."""
        form = PersonajeForm({
            'tipo': 'GUERRERO',
            'nombre': 'GuerreroTest',
            'nivel': 5,
            'vida': 100,
            'vida_max': 100,
            'armadura': 10,
        })
        self.assertTrue(form.is_valid())
    
    def test_form_valido_mago(self):
        """Verifica que el formulario es valido con datos de mago."""
        form = PersonajeForm({
            'tipo': 'MAGO',
            'nombre': 'MagoTest',
            'nivel': 3,
            'vida': 80,
            'vida_max': 80,
            'mana': 50,
        })
        self.assertTrue(form.is_valid())
    
    def test_form_valido_arquero(self):
        """Verifica que el formulario es valido con datos de arquero."""
        form = PersonajeForm({
            'tipo': 'ARQUERO',
            'nombre': 'ArqueroTest',
            'nivel': 4,
            'vida': 90,
            'vida_max': 90,
            'precision': 85,
        })
        self.assertTrue(form.is_valid())
    
    def test_form_nombre_vacio(self):
        """Verifica que el formulario rechaza nombre vacio."""
        form = PersonajeForm({
            'tipo': 'GUERRERO',
            'nombre': '',
            'nivel': 1,
            'vida': 100,
            'vida_max': 100,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('nombre', form.errors)
    
    def test_form_nivel_negativo(self):
        """Verifica que el formulario rechaza nivel negativo."""
        form = PersonajeForm({
            'tipo': 'GUERRERO',
            'nombre': 'TestNivel',
            'nivel': -1,
            'vida': 100,
            'vida_max': 100,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('nivel', form.errors)
    
    def test_form_tipo_vacio(self):
        """Verifica que el formulario requiere seleccionar un tipo."""
        form = PersonajeForm({
            'tipo': '',
            'nombre': 'TestTipo',
            'nivel': 1,
            'vida': 100,
            'vida_max': 100,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('tipo', form.errors)
    
    def test_form_save_guerrero(self):
        """Verifica que se puede guardar un guerrero desde el formulario."""
        form = PersonajeForm({
            'tipo': 'GUERRERO',
            'nombre': 'FormGuerrero',
            'nivel': 2,
            'vida': 100,
            'vida_max': 100,
            'armadura': 15,
        })
        
        if form.is_valid():
            personaje = form.save()
            self.assertEqual(personaje.nombre, 'FormGuerrero')
            self.assertEqual(personaje.tipo, 'GUERRERO')
            self.assertEqual(personaje.armadura, 15)
            personaje.delete()
    
    def test_form_save_mago(self):
        """Verifica que se puede guardar un mago desde el formulario."""
        form = PersonajeForm({
            'tipo': 'MAGO',
            'nombre': 'FormMago',
            'nivel': 2,
            'vida': 80,
            'vida_max': 80,
            'mana': 60,
        })
        
        if form.is_valid():
            personaje = form.save()
            self.assertEqual(personaje.nombre, 'FormMago')
            self.assertEqual(personaje.tipo, 'MAGO')
            self.assertEqual(personaje.mana, 60)
            personaje.delete()
    
    def test_form_save_arquero(self):
        """Verifica que se puede guardar un arquero desde el formulario."""
        form = PersonajeForm({
            'tipo': 'ARQUERO',
            'nombre': 'FormArquero',
            'nivel': 2,
            'vida': 90,
            'vida_max': 90,
            'precision': 75,
        })
        
        if form.is_valid():
            personaje = form.save()
            self.assertEqual(personaje.nombre, 'FormArquero')
            self.assertEqual(personaje.tipo, 'ARQUERO')
            self.assertEqual(personaje.precision, 75)
            personaje.delete()
    
    def test_form_defaults_guerrero(self):
        """Verifica que el guerrero tiene valores por defecto correctos."""
        form = PersonajeForm({
            'tipo': 'GUERRERO',
            'nombre': 'GuerreroDefault',
            'nivel': 1,
            'vida': 100,
            'vida_max': 100,
        })
        
        if form.is_valid():
            personaje = form.save()
            self.assertEqual(personaje.armadura, 5)
            personaje.delete()
    
    def test_form_defaults_mago(self):
        """Verifica que el mago tiene valores por defecto correctos."""
        form = PersonajeForm({
            'tipo': 'MAGO',
            'nombre': 'MagoDefault',
            'nivel': 1,
            'vida': 80,
            'vida_max': 80,
        })
        
        if form.is_valid():
            personaje = form.save()
            self.assertEqual(personaje.mana, 50)
            personaje.delete()
    
    def test_form_defaults_arquero(self):
        """Verifica que el arquero tiene valores por defecto correctos."""
        form = PersonajeForm({
            'tipo': 'ARQUERO',
            'nombre': 'ArqueroDefault',
            'nivel': 1,
            'vida': 90,
            'vida_max': 90,
        })
        
        if form.is_valid():
            personaje = form.save()
            self.assertEqual(personaje.precision, 80)
            personaje.delete()
