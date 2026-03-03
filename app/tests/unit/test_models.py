import pytest
from django.test import TestCase
from app.models import Personaje
from app.services import (
    crear_personaje,
    obtener_personaje,
    listar_personajes,
    actualizar_personaje,
    borrar_personaje,
    personaje_a_dict,
)


@pytest.mark.unit
@pytest.mark.django_db
class TestPersonajeModel(TestCase):
    """Tests para el modelo Personaje."""
    
    def test_crear_personaje_base(self):
        """Verifica que se puede crear un personaje base."""
        p = Personaje.objects.create(
            tipo='PERSONAJE',
            nombre='Heroe1',
            nivel=1,
            vida=100,
            vida_max=100
        )
        self.assertEqual(p.nombre, 'Heroe1')
        self.assertEqual(p.tipo, 'PERSONAJE')
        self.assertEqual(p.nivel, 1)
        self.assertTrue(p.esta_vivo())
    
    def test_crear_guerrero(self):
        """Verifica que se puede crear un guerrero con armadura."""
        p = Personaje.objects.create(
            tipo='GUERRERO',
            nombre='Guerrero1',
            nivel=1,
            vida=100,
            vida_max=100,
            armadura=10
        )
        self.assertEqual(p.tipo, 'GUERRERO')
        self.assertEqual(p.armadura, 10)
    
    def test_crear_mago(self):
        """Verifica que se puede crear un mago con mana."""
        p = Personaje.objects.create(
            tipo='MAGO',
            nombre='Mago1',
            nivel=1,
            vida=80,
            vida_max=80,
            mana=50
        )
        self.assertEqual(p.tipo, 'MAGO')
        self.assertEqual(p.mana, 50)
    
    def test_crear_arquero(self):
        """Verifica que se puede crear un arquero con precision."""
        p = Personaje.objects.create(
            tipo='ARQUERO',
            nombre='Arquero1',
            nivel=1,
            vida=90,
            vida_max=90,
            precision=85
        )
        self.assertEqual(p.tipo, 'ARQUERO')
        self.assertEqual(p.precision, 85)
    
    def test_esta_vivo(self):
        """Verifica el metodo esta_vivo."""
        p = Personaje.objects.create(
            tipo='PERSONAJE',
            nombre='TestVivo',
            nivel=1,
            vida=50,
            vida_max=100
        )
        self.assertTrue(p.esta_vivo())
        
        p.vida = 0
        self.assertFalse(p.esta_vivo())
    
    def test_recibir_danio(self):
        """Verifica que recibir_danio reduce la vida correctamente."""
        p = Personaje.objects.create(
            tipo='PERSONAJE',
            nombre='TestDanio',
            nivel=1,
            vida=100,
            vida_max=100
        )
        p.recibir_danio(30)
        self.assertEqual(p.vida, 70)
    
    def test_recibir_danio_negativo_lanza_error(self):
        """Verifica que recibir_danio lanza error con dano negativo."""
        p = Personaje.objects.create(
            tipo='PERSONAJE',
            nombre='TestDanioNeg',
            nivel=1,
            vida=100,
            vida_max=100
        )
        with self.assertRaises(ValueError):
            p.recibir_danio(-10)
    
    def test_curar(self):
        """Verifica que curar restaura vida."""
        p = Personaje.objects.create(
            tipo='PERSONAJE',
            nombre='TestCurar',
            nivel=1,
            vida=30,
            vida_max=100
        )
        p.curar(50)
        self.assertEqual(p.vida, 80)
    
    def test_curar_no_supera_maximo(self):
        """Verifica que curar no supera la vida maxima."""
        p = Personaje.objects.create(
            tipo='PERSONAJE',
            nombre='TestCurarMax',
            nivel=1,
            vida=90,
            vida_max=100
        )
        p.curar(50)
        self.assertEqual(p.vida, 100)
    
    def test_subir_nivel(self):
        """Verifica que subir_nivel aumenta nivel, vida_max y vida."""
        p = Personaje.objects.create(
            tipo='PERSONAJE',
            nombre='TestSubir',
            nivel=1,
            vida=100,
            vida_max=100
        )
        p.subir_nivel()
        
        self.assertEqual(p.nivel, 2)
        self.assertEqual(p.vida_max, 110)
    
    def test_ataque(self):
        """Verifica que ataque devuelve 10 + nivel."""
        p = Personaje.objects.create(
            tipo='PERSONAJE',
            nombre='TestAtaque',
            nivel=5,
            vida=100,
            vida_max=100
        )
        self.assertEqual(p.ataque(), 15)
    
    def test_unique_nombre(self):
        """Verifica que no se pueden crear personajes con el mismo nombre."""
        Personaje.objects.create(
            tipo='PERSONAJE',
            nombre='Unico',
            nivel=1,
            vida=100,
            vida_max=100
        )
        with self.assertRaises(Exception):
            Personaje.objects.create(
                tipo='PERSONAJE',
                nombre='Unico',
                nivel=1,
                vida=100,
                vida_max=100
            )


@pytest.mark.unit
@pytest.mark.django_db
class TestGuerrero(TestCase):
    """Tests especificos para el tipo Guerrero."""
    
    def test_guerrero_recibe_danio_reducido(self):
        """Verifica que el guerrero reduce el dano por armadura."""
        p = Personaje.objects.create(
            tipo='GUERRERO',
            nombre='GuerreroDanio',
            nivel=1,
            vida=100,
            vida_max=100,
            armadura=10
        )
        p.recibir_danio(30)
        self.assertEqual(p.vida, 80)
    
    def test_guerrero_danio_no_negativo(self):
        """Verifica que el dano efectivo no puede ser negativo."""
        p = Personaje.objects.create(
            tipo='GUERRERO',
            nombre='GuerreroArmadura',
            nivel=1,
            vida=100,
            vida_max=100,
            armadura=50
        )
        p.recibir_danio(10)
        self.assertEqual(p.vida, 100)


@pytest.mark.unit
@pytest.mark.django_db
class TestMago(TestCase):
    """Tests especificos para el tipo Mago."""
    
    def test_ataque_especial_con_mana(self):
        """Verifica que ataque especial consume mana y hace dano doble."""
        p = Personaje.objects.create(
            tipo='MAGO',
            nombre='MagoAtaque',
            nivel=5,
            vida=100,
            vida_max=100,
            mana=50
        )
        dano = p.ataque_especial()
        self.assertEqual(dano, 30)
        self.assertEqual(p.mana, 40)
    
    def test_ataque_especial_sin_mana(self):
        """Verifica que ataque especial retorna 0 sin mana."""
        p = Personaje.objects.create(
            tipo='MAGO',
            nombre='MagoSinMana',
            nivel=5,
            vida=100,
            vida_max=100,
            mana=5
        )
        dano = p.ataque_especial()
        self.assertEqual(dano, 0)


@pytest.mark.unit
@pytest.mark.django_db
class TestArquero(TestCase):
    """Tests especificos para el tipo Arquero."""
    
    def test_arquero_ataque_precision(self):
        """Verifica que el arquero puede fallar ataques."""
        p = Personaje.objects.create(
            tipo='ARQUERO',
            nombre='ArqueroPrecision',
            nivel=5,
            vida=100,
            vida_max=100,
            precision=0
        )
        dano = p.ataque()
        self.assertEqual(dano, 0)


@pytest.mark.unit
@pytest.mark.django_db
class TestPersonajeService(TestCase):
    """Tests para el servicio de personajes."""
    
    def setUp(self):
        """Configuracion inicial para cada test."""
        self.personajes_creados = []
    
    def tearDown(self):
        """Limpieza despues de cada test."""
        Personaje.objects.all().delete()
    
    def test_crear_personaje_servicio(self):
        """Verifica que el servicio crea personajes correctamente."""
        p = crear_personaje('GUERRERO', 'ServicioGuerrero', nivel=3, armadura=15)
        self.assertEqual(p.nombre, 'ServicioGuerrero')
        self.assertEqual(p.tipo, 'GUERRERO')
        self.assertEqual(p.nivel, 3)
        self.assertEqual(p.armadura, 15)
    
    def test_crear_mago_servicio(self):
        """Verifica que el servicio crea magos."""
        p = crear_personaje('MAGO', 'ServicioMago', mana=100)
        self.assertEqual(p.tipo, 'MAGO')
        self.assertEqual(p.mana, 100)
    
    def test_crear_arquero_servicio(self):
        """Verifica que el servicio crea arqueros."""
        p = crear_personaje('ARQUERO', 'ServicioArquero', precision=90)
        self.assertEqual(p.tipo, 'ARQUERO')
        self.assertEqual(p.precision, 90)
    
    def test_obtener_personaje(self):
        """Verifica que se puede obtener un personaje por ID."""
        p = crear_personaje('PERSONAJE', 'Buscar')
        encontrado = obtener_personaje(p.id)
        self.assertEqual(encontrado.nombre, 'Buscar')
    
    def test_obtener_personaje_inexistente(self):
        """Verifica que obtener_personaje retorna None para ID inexistente."""
        resultado = obtener_personaje(99999)
        self.assertIsNone(resultado)
    
    def test_listar_personajes(self):
        """Verifica que listar_personajes retorna todos los personajes."""
        Personaje.objects.all().delete()
        
        crear_personaje('PERSONAJE', 'Personaje1')
        crear_personaje('GUERRERO', 'Personaje2')
        crear_personaje('MAGO', 'Personaje3')
        
        lista = listar_personajes()
        self.assertEqual(len(lista), 3)
    
    def test_actualizar_personaje(self):
        """Verifica que se pueden actualizar personajes."""
        p = crear_personaje('PERSONAJE', 'Actualizar')
        actualizado = actualizar_personaje(p.id, nombre='Actualizado', nivel=10)
        
        self.assertEqual(actualizado.nombre, 'Actualizado')
        self.assertEqual(actualizado.nivel, 10)
    
    def test_borrar_personaje(self):
        """Verifica que se pueden borrar personajes."""
        p = crear_personaje('PERSONAJE', 'Borrar')
        resultado = borrar_personaje(p.id)
        
        self.assertTrue(resultado)
        self.assertIsNone(obtener_personaje(p.id))
    
    def test_borrar_personaje_inexistente(self):
        """Verifica que borrar_personaje retorna False para ID inexistente."""
        resultado = borrar_personaje(99999)
        self.assertFalse(resultado)
    
    def test_personaje_a_dict(self):
        """Verifica la serializacion a diccionario."""
        p = crear_personaje('GUERRERO', 'DictGuerrero', nivel=5, armadura=20)
        data = personaje_a_dict(p)
        
        self.assertEqual(data['nombre'], 'DictGuerrero')
        self.assertEqual(data['tipo'], 'GUERRERO')
        self.assertEqual(data['nivel'], 5)
        self.assertEqual(data['armadura'], 20)
    
    def test_tipos_validos(self):
        """Verifica que se aceptan todos los tipos validos."""
        tipos = ['PERSONAJE', 'GUERRERO', 'MAGO', 'ARQUERO']
        for tipo in tipos:
            p = crear_personaje(tipo, f'Personaje{tipo}')
            self.assertEqual(p.tipo, tipo)
    
    def test_tipo_invalido(self):
        """Verifica que un tipo invalido lanza error."""
        with self.assertRaises(ValueError):
            crear_personaje('INVALIDO', 'TestInvalido')
