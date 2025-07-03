document.addEventListener("DOMContentLoaded", function(){
    
    // Select2 Configuration
    let opciones = {
        placeholder: "----------",
        allowClear: true,
        containerCssClass : 'select form-select',
        theme: "bootstrap-5",
        width: 'auto',
    }
    
    $("#id_clase").select2(opciones);


    // Buscamos formulario para dia de clase
    $("#id_clase").on("select2:select", () => get_form( $("#id_clase").val() ));


    // Reactivacion con valores anteriores
    if( $("#id_clase").val() ) {
        val = $("#id_clase").val();

        $("#id_clase").val(null).trigger("change");
        $("#id_clase").val(val).trigger("change");

        get_form(val);   
    }


    // Al limpiar el campo, se resetea el resto.
    $("#id_clase").on("select2:clear", () => {
        document.querySelector("#dias-form").innerHTML = "";

        document.querySelector("#dias-form").innerHTML = "<p>Seleccione una clase primero.</p>";

        document.querySelector("#submit-button").disabled = true;
    });

});

async function get_form(clase_id) {

    let url = document.querySelector("form").dataset.form;
    let csrf_token = document.querySelector("[name=csrfmiddlewaretoken]").value;

    let request = {
        method: "POST",
        headers: {'X-CSRFToken': csrf_token},
        mode: 'same-origin',
        body: JSON.stringify({"pk": clase_id}),
    }
    
    let response = await fetch(url, request);
    let obj      = await response.json();

    render_form(obj);
    
    return obj;
}

function render_form(forms) {

    let dias_form = forms.dias_form;

    document.querySelector("#dias-form").innerHTML = "";
    document.querySelector("#dias-form").innerHTML = dias_form;

    document.querySelector("#submit-button").disabled = false;
}
