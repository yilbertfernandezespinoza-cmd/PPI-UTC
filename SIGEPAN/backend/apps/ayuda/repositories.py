from apps.ayuda.models import Ayuda


class AyudaRepository:
    """
    Repositorio encargado de las operaciones de acceso a datos
    para el módulo de Ayudas.
    """

    @staticmethod
    def listar():
        """
        Retorna todas las ayudas ordenadas por módulo, orden y título.
        """
        return Ayuda.objects.select_related("modulo").all()

    @staticmethod
    def obtener_por_id(id_ayuda):
        """
        Obtiene una ayuda por su identificador.
        """
        return (
            Ayuda.objects
            .select_related("modulo")
            .filter(id_ayuda=id_ayuda)
            .first()
        )

    @staticmethod
    def crear(**datos):
        """
        Crea una nueva ayuda.
        """
        return Ayuda.objects.create(**datos)

    @staticmethod
    def actualizar(ayuda, **datos):
        """
        Actualiza una ayuda existente.
        """
        for campo, valor in datos.items():
            setattr(ayuda, campo, valor)

        ayuda.save()
        return ayuda

    @staticmethod
    def cambiar_estado(ayuda, estado):
        """
        Activa o inactiva una ayuda.
        """
        ayuda.estado = estado
        ayuda.save(update_fields=["estado"])
        return ayuda