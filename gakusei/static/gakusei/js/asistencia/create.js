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


    // Buscamos Estudiantes y formulario para dia de clase
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
        document.querySelector("#estudiantes-formset").innerHTML = "";

        document.querySelector("#dias-form").innerHTML = "<p>Seleccione una clase primero.</p>";

        document.querySelector("#submit-button").disabled = true;
    });


    // Intersepcion de los datos enviados por el formulario
    document.querySelector("#asistencia-form").addEventListener("submit", function(event) {
        event.preventDefault();

        let form = event.target;
        let form_data = new FormData(form);

        let status, error_form, url_redirect;
        fetch(form.action, {
            method: form.method,
            body: form_data,
        })
        .then(r => {
            status = r.ok;
            return r.json();
        })
        .then(r => {
            if(status){
                url_redirect = r.url_redirect;
            }
            else {
                error_form = r.error_form;
            }
        })
        .finally(() => {
            if(status){                
                window.location.href = url_redirect;
            }
            else {
                document.querySelector("#estudiante-presentes").innerHTML = "";
                document.querySelector("#estudiante-presentes").innerHTML = error_form;
            }
        });
        

    });

});

async function get_form(clase_id) {

    let url = document.querySelector("#asistencia-form").dataset.form;
    let csrf_token = document.querySelector("[name=csrfmiddlewaretoken]").value;

    let request = {
        method: "POST",
        headers: {'X-CSRFToken': csrf_token},
        mode: 'same-origin',
        body: JSON.stringify({"pk": clase_id}),
    }
    
    let response = await fetch(url, request);
    let obj      = await response.json();

    render_forms(obj);
    
    return obj;
}

function render_forms(forms) {

    let dias_form = forms.dias_form;
    let estudiantes_formset;
    
    if (forms.estudiantes_count) {
        estudiantes_formset = forms.formset;
    } else {
        estudiantes_formset = "<p><i>Clase sin estudiantes registrados.</i></p>";
    }

    document.querySelector("#dias-form").innerHTML = "";
    document.querySelector("#dias-form").innerHTML = dias_form;

    document.querySelector("#estudiantes-formset").innerHTML = "";
    document.querySelector("#estudiantes-formset").innerHTML = `<h3>Estudiantes</h3>${estudiantes_formset}`;

    document.querySelector("#submit-button").disabled = false;

}
