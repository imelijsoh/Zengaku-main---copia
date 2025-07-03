document.addEventListener("DOMContentLoaded", function() {
    
    // Select2 Configuration
    let opciones = {
        placeholder: "----------",
        allowClear: true,
        containerCssClass : 'select form-select',
        theme: "bootstrap-5",
        width: 'auto',
    }

    $("#id_sensei").select2(opciones);
    $("#id_curso").select2(opciones);
    $("#id_sede").select2(opciones);
});