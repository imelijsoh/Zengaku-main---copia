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

    let opciones_clase = opciones;
    opciones_clase.placeholder = "Seleccione primero un estudiante.";
    opciones_clase.disabled = true;
    opciones_clase.data = null;

    $("#id_clase").select2(opciones_clase);


    $("#id_estudiante").on("select2:select", () => {
        get_clases( $("#id_estudiante").val() );
        if (document.querySelector("#mensualidad")) {
            document.querySelector("#mensualidad").innerHTML = "";
        }
        document.querySelector("#mensualidad-tabla").innerHTML = "";
    });


    $("#id_estudiante").on("select2:clear", () => {
        $("#id_clase").select2(opciones_clase).val(null).change();
        if (document.querySelector("#mensualidad")) {
            document.querySelector("#mensualidad").innerHTML = "";
        }
        document.querySelector("#mensualidad-tabla").innerHTML = "";
    });


    if( $("#id_estudiante").val() && $("#id_clase").val() ) {
        val_estudiante = $("#id_estudiante").val();
        val_clase = $("#id_clase").val();

        get_clases( val_estudiante, val_clase );
        get_mensualidad();
    }

});



async function get_clases(id_estudiante, id_clase=null){

    let url = document.querySelector("#pago-form").dataset.get_clases;
    let csrf_token = document.querySelector("[name=csrfmiddlewaretoken]").value;

    let request = {
        method: "POST",
        headers: {'X-CSRFToken': csrf_token},
        mode: 'same-origin',
        body: JSON.stringify({"pk": id_estudiante}),
    }

    let response = await fetch(url, request);
    let obj      = await response.json();
    
    let status = response.ok;
    let clases = obj.results;

    let opciones = {
        placeholder: "----------",
        allowClear: true,
        containerCssClass : 'select form-select',
        theme: "bootstrap-5",
        width: 'auto',
        disabled: false,
        data: clases,
    } 

    if($("#id_clase").hasClass("select2-hidden-accessible")){
        $("#id_clase").empty().select2("destroy");
        $("#id_clase").off("select2:select");
    }

    $("#id_clase").select2(opciones).val(id_clase).change();
    $("#id_clase").on("select2:select", () => get_mensualidad());

    $("#id_clase").on("select2:clear", () => {
        document.querySelector("#mensualidad").innerHTML = "";
        document.querySelector("#mensualidad-tabla").innerHTML = "";
    });
}


async function get_mensualidad() {

    let url = document.querySelector("#mensualidad-tabla").dataset.mensualidad;
    let csrf_token = document.querySelector("[name=csrfmiddlewaretoken]").value;

    let request = {
        method: "POST",
        headers: {'X-CSRFToken': csrf_token},
        mode: 'same-origin',
        body: JSON.stringify({"estudiante": $("#id_estudiante").val(), "clase": $("#id_clase").val()}),
    }

    let response = await fetch(url, request);
    let obj      = await response.json();
    
    let status = response.ok;
    let mensualidad = obj.mensualidad;
    let solvencias  = obj.solvencias;

    tabla_solvencias(solvencias);


    let p_mensualidad;

    if (document.querySelector("#mensualidad")) {
        p_mensualidad = document.querySelector("#mensualidad");
    } else {
        p_mensualidad = document.createElement("p");
    }

    p_mensualidad.innerText = `Mensualidad Actual del Estudiante: ${mensualidad}$`;
    p_mensualidad.id = "mensualidad";
    p_mensualidad.className = "mt-2 fw-bold text-end";

    document.querySelector("#div_id_monto_pagado").append(p_mensualidad);

}

function tabla_solvencias(solvencias_data) {

    let nombre = solvencias_data.estudiante;
    let solvencias = solvencias_data.solvencias;

    let tabla = document.createElement("table");
    let thead = document.createElement("thead");
    let tbody = document.createElement("tbody");


    // Clases
    tabla.className = "table table-striped table-hover table-bordered mt-4";
    thead.className = "table-primary";


    // Encabezados
    let trHeadNombre = document.createElement("tr");
    let thNombre     = document.createElement("th");
    
    thNombre.textContent = nombre;
    thNombre.className = "text-center";
    thNombre.colSpan = 4;

    trHeadNombre.appendChild(thNombre);
    thead.appendChild(trHeadNombre); 


    let encabezados = ["Mes", "Status", "Precio", "Abonado"];
    let trHeadSolvencia = document.createElement("tr");

    encabezados.forEach(celda => {
        let th = document.createElement("th");
        th.textContent = celda;
        trHeadSolvencia.appendChild(th);
    });

    thead.appendChild(trHeadSolvencia); 


    // Body
    if(Object.keys(solvencias).length === 0){
        
        let tr = document.createElement("tr");
        let td = document.createElement("td");

        td.innerHTML = "<i>Sin Solvencias Registradas</i>";
        td.colSpan = 4;

        tr.appendChild(td);
        tbody.appendChild(tr);
        
    }else{
    
        solvencias.forEach(item => {
            let tr = document.createElement("tr");

            Object.values(item).forEach(celda => {
                let td = document.createElement("td");

                if (item.pagado == 'Pagado' ) {
                    td.className = "bg-info-subtle";
                }
                else if (item.pagado == 'Abonado' ) {
                    td.className = "bg-warning-subtle";
                }
                else if (item.pagado == 'Sin Pagar' ) {
                    td.className = "bg-danger-subtle";
                }

                td.textContent = celda;
                tr.appendChild(td);
            });

            tbody.appendChild(tr);
        });

        
    }

    // Combinacion
    tabla.appendChild(thead);
    tabla.appendChild(tbody);

    // Pegado
    document.querySelector("#mensualidad-tabla").innerHTML = "";
    document.querySelector("#mensualidad-tabla").appendChild(tabla);
    
}