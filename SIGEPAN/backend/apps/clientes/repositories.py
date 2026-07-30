# Repositorios del módulo
from .models import Cliente


class ClienteRepository:
    """
    Repositorio para el acceso a datos del módulo Clientes.
    """

    @staticmethod
    def listar():
        """
        Obtiene todos los clientes.
        """

        return (
            Cliente.objects
            .all()
            .order_by(
                "nombre",
                "apellido1",
            )
        )

    @staticmethod
    def obtener(id_cliente):
        """
        Obtiene un cliente por su identificador.
        """

        return Cliente.objects.get(
            id_cliente=id_cliente
        )

    @staticmethod
    def crear(**datos):
        """
        Crea un nuevo cliente.
        """

        return Cliente.objects.create(
            **datos
        )

    @staticmethod
    def actualizar(cliente):
        """
        Guarda los cambios de un cliente.
        """

        cliente.save()

        return cliente

    @staticmethod
    def existe_identificacion(
        identificacion,
        excluir_id=None,
    ):
        """
        Verifica si ya existe una identificación registrada.
        """

        consulta = Cliente.objects.filter(
            identificacion=identificacion
        )

        if excluir_id:

            consulta = consulta.exclude(
                id_cliente=excluir_id
            )

        return consulta.exists()