from django.core.exceptions import ValidationError

from .repositories import ClienteRepository


class ClienteService:

    @staticmethod
    def listar():
        return ClienteRepository.listar()

    @staticmethod
    def obtener(id_cliente):
        return ClienteRepository.obtener(id_cliente)

    @staticmethod
    def crear(datos):

        identificacion = datos["identificacion"]

        if ClienteRepository.existe_identificacion(identificacion):
            raise ValidationError(
                "Ya existe un cliente con esa identificación."
            )

        return ClienteRepository.crear(**datos)

    @staticmethod
    def actualizar(id_cliente, datos):

        cliente = ClienteRepository.obtener(id_cliente)

        identificacion = datos["identificacion"]

        if ClienteRepository.existe_identificacion(
            identificacion,
            excluir_id=id_cliente,
        ):
            raise ValidationError(
                "Ya existe un cliente con esa identificación."
            )

        for campo, valor in datos.items():
            setattr(cliente, campo, valor)

        return ClienteRepository.actualizar(cliente)

    @staticmethod
    def cambiar_estado(id_cliente):

        cliente = ClienteRepository.obtener(id_cliente)

        if cliente is None:
            raise ValidationError(
                "El cliente no existe."
            )

        cliente.estado = not cliente.estado

        return ClienteRepository.actualizar(cliente)