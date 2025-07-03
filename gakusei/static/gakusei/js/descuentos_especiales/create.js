document.addEventListener("DOMContentLoaded", function(){
    
    // Select2 Configuration
    let opciones = {
        placeholder: "----------",
        allowClear: true,
        containerCssClass : 'select form-select',
        theme: "bootstrap-5",
        width: 'auto',
    }
    
    $("#id_estudiante").select2(opciones);


});
