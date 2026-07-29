from apps.ayuda.repositories import AyudaRepository
from apps.configuracion.models import Modulo


class AyudaService:
    """
    Servicio encargado de la lógica de negocio
    del módulo de Ayudas.
    """

    @staticmethod
    def listar():
        return AyudaRepository.listar()

    @staticmethod
    def obtener_por_id(id_ayuda):
        return AyudaRepository.obtener_por_id(id_ayuda)

    @staticmethod
    def crear(modulo_id, pantalla, titulo, contenido, icono=None, orden=1):
        """
        Crea una nueva ayuda.
        """

        modulo = Modulo.objects.filter(id_modulo=modulo_id).first()

        if not modulo:
            raise ValueError("El módulo seleccionado no existe.")

        ayuda_existente = AyudaRepository.listar().filter(
            modulo=modulo,
            pantalla=pantalla
        ).first()

        if ayuda_existente:
            raise ValueError(
                "Ya existe una ayuda registrada para esa pantalla en este módulo."
            )

        return AyudaRepository.crear(
            modulo=modulo,
            pantalla=pantalla,
            titulo=titulo,
            contenido=contenido,
            icono=icono,
            orden=orden
        )

    @staticmethod
    def actualizar(
        id_ayuda,
        modulo_id,
        pantalla,
        titulo,
        contenido,
        icono,
        orden
    ):

        ayuda = AyudaRepository.obtener_por_id(id_ayuda)

        if not ayuda:
            raise ValueError("La ayuda no existe.")

        modulo = Modulo.objects.filter(id_modulo=modulo_id).first()

        if not modulo:
            raise ValueError("El módulo seleccionado no existe.")

        existe = AyudaRepository.listar().filter(
            modulo=modulo,
            pantalla=pantalla
        ).exclude(
            id_ayuda=id_ayuda
        ).first()

        if existe:
            raise ValueError(
                "Ya existe una ayuda registrada para esa pantalla."
            )

        return AyudaRepository.actualizar(
            ayuda,
            modulo=modulo,
            pantalla=pantalla,
            titulo=titulo,
            contenido=contenido,
            icono=icono,
            orden=orden
        )

    @staticmethod
    def cambiar_estado(id_ayuda):

        ayuda = AyudaRepository.obtener_por_id(id_ayuda)

        if not ayuda:
            raise ValueError("La ayuda no existe.")

        nuevo_estado = not ayuda.estado

        AyudaRepository.cambiar_estado(
            ayuda,
            nuevo_estado
        )

        return nuevo_estado