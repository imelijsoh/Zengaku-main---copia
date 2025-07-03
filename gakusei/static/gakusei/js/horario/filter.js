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
    $("#id_dia_semana").select2(opciones);
});