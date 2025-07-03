document.addEventListener("DOMContentLoaded", function() {
    
    // Select2 Configuration
    let opciones = {
        placeholder: "----------",
        allowClear: true,
        containerCssClass : 'select form-select',
        theme: "bootstrap-5",
        width: 'auto',
    }

    $("#id_clase").select2(opciones);

    document.querySelector("#horario-form").addEventListener("submit", () => {

        // Para cuando sea asignacion de clases por GET
        document.querySelector("#id_clase").disabled  = false;
    });
});