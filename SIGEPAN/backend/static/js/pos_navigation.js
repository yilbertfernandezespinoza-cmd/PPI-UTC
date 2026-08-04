/**
 * SIGEPAN - Master Navigation Controller
 * Controla el flujo de retorno y rastreo de origen para todos los módulos del POS.
 */
document.addEventListener('DOMContentLoaded', function () {
    
    // 1. Rastreo automático de origen
    // Cualquier enlace con [data-track-origin] guardará la ruta actual antes de navegar.
    document.querySelectorAll('[data-track-origin]').forEach(link => {
        link.addEventListener('click', function () {
            const currentPath = window.location.pathname + window.location.search;
            sessionStorage.setItem('pos_return_path', currentPath);
        });
    });

    // 2. Manejador universal de botones "Volver"
    // Cualquier botón con la clase .btn-volver utilizará la ruta guardada o un respaldo seguro.
    document.querySelectorAll('.btn-volver').forEach(btn => {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            
            // Permite definir un respaldo específico en el HTML usando data-fallback="..."
            const customFallback = this.getAttribute('data-fallback') || '/ventas/crear/';
            
            // Obtiene la ruta almacenada o usa el respaldo
            const returnPath = sessionStorage.getItem('pos_return_path') || customFallback;
            
            // Limpia la memoria temporal para evitar bucles
            sessionStorage.removeItem('pos_return_path');
            
            // Redirige al destino correcto
            window.location.href = returnPath;
        });
    });
});