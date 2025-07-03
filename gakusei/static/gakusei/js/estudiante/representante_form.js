$(document).ready(function() {

    // Select2 configuration
    let opciones = {
        placeholder: "Seleccione un Representante",
        allowClear: true,
        containerCssClass : 'select form-select',
        theme: "bootstrap-5",
        width: 'auto',
    }
    
    $("#id_representante").select2(opciones);


    // Registro de Representante (Nueva ventana)
    let registro_representante = document.querySelector("#registro-repesentante");
    let url = registro_representante.dataset.representante_url;

    registro_representante.onclick = () => window.open(url, "registroRep", "popup=true");

});


async function get_representantes() {

    if ($("#id_representante").hasClass("select2-hidden-accessible")) {
        $("#id_representante").select2('destroy');
    }
    
    let url = document.querySelector("#registro-repesentante").dataset.representante_get;

    let response       = await fetch(url);
    let representantes = await response.json();
    
    $("#id_representante").empty();
    $("#id_representante").select2({
        data: representantes.results,
        placeholder: "Seleccione un Representante",
        allowClear: true,
        containerCssClass : 'select form-select',
        theme: "bootstrap-5",
        width: 'auto',
    });

}

async function recibirRepresentante(representante_id) {

    await get_representantes();
    
    $("#id_representante").val(representante_id).trigger("change");

}
