// Numero
var precio_clase = false;

// Objecto JS
var beca  = false;

// Numero
var descuento  = false;


$(document).ready(function() {

    // Select2 configuration
    let opciones = {
        placeholder: "----------",
        allowClear: true,
        containerCssClass : 'select form-select',
        theme: "bootstrap-5",
        width: 'auto',
    }
    
    $("#id_clase").select2(opciones);
    $("#id_estudiante").select2(opciones);
    

    // Al limpiar Clase
    $("#id_clase").on("select2:clear", () => {
        // Agregado esta linea para asegurar el clear
        $('#id_clase').val(null).trigger('change');

        precio_clase = false;
        document.querySelector("#clase-data").innerText = "";

        calculo_precio();
    });

    // Al limpiar el Estudiante
    $("#id_estudiante").on("select2:clear", () => {
        $('#id_estudiante').val(null).trigger('change');

        beca = false;
        descuento = false;
        document.querySelector("#estudiante-beca").innerText = "";
        document.querySelector("#estudiante-beca").className = "";
        document.querySelector("#estudiante-descuento").innerText = "";
        document.querySelector("#estudiante-descuento").className = "";

        calculo_precio();
    });

    // Obtenemos los precios y becas a partir de las funciones asincronas
    $("#id_clase").on("select2:select", (e) => get_price_clase(e));
    $("#id_estudiante").on("select2:select", (e) => get_price_estudiante(e));


    // Recuperamos datos anteriores y reactivamos las funciones de obtenion de precios
    if( $("#id_clase").val() ) {
        val = $("#id_clase").val();

        $("#id_clase").val(null).trigger("change");
        $("#id_clase").val(val).trigger("change");

        // Objeto que simula ser un evento
        let e = {"params": { "data": {"id": val} }}
        get_price_clase(e);   
    }

    if( $("#id_estudiante").val() ) {
        val = $("#id_estudiante").val();

        $("#id_estudiante").val(null).trigger("change");
        $("#id_estudiante").val(val).trigger("change");

        let e = {"params": { "data": {"id": val} }}
        get_price_estudiante(e);   
    }


    document.querySelector("#inscripciones-form").addEventListener("submit", () => {

        document.querySelector("#id_clase").disabled  = false;
        document.querySelector("#id_estudiante").disabled  = false;
    });
});

async function get_price_clase(e) {
    let url = document.querySelector("#inscripciones-form").dataset.clase_url;
    let clase = await get_api_data(e, url);
    
    precio_clase = clase.precio;

    let p;

    if (document.querySelector("#clase-data")) {
        p = document.querySelector("#clase-data");
    } else {
        p = document.createElement("p");
    }
    
    p.innerText = `Precio de la clase: ${clase.precio}$`;
    p.id = "clase-data";
    p.className = "mt-2";

    document.querySelector("#div_id_clase").append(p);

    calculo_precio();
}

async function get_price_estudiante(e) {
    let url = document.querySelector("#inscripciones-form").dataset.estudiante_url;
    let estudiante = await get_api_data(e, url);

    let beca_data, descuento_data;

    let p_beca, p_descuento;



    if (document.querySelector("#estudiante-beca")) {
        p_beca = document.querySelector("#estudiante-beca");
    } else {
        p_beca = document.createElement("p");
    }

    if (document.querySelector("#estudiante-descuento")) {
        p_descuento = document.querySelector("#estudiante-descuento");
    } else {
        p_descuento = document.createElement("p");
    }

    // Descuento -> Beca

    if (estudiante.descuento) {
        // Estudiante -> Descuento Especial -> Cuanto es el descuento.
        descuento_data = estudiante.descuento.descuento;

        descuento = descuento_data;

        p_descuento.innerText = `Descuento: ${descuento_data}$`;
        p_descuento.id = "estudiante-descuento";
        if (estudiante.beca) {
            p_descuento.className = "mt-2 mb-0";
        } else {
            p_descuento.className = "mt-2";
        }
        
        document.querySelector("#div_id_estudiante").append(p_descuento);

    } else {
        descuento = false;

        if (document.querySelector("#estudiante-descuento")) {
            document.querySelector("#estudiante-descuento").innerText = "";
            document.querySelector("#estudiante-descuento").className = "";
        }
    }

    if (estudiante.beca) {
        
        // Estudiante -> Beca.
        beca_data = estudiante.beca;
        
        // Declaramos variable global
        beca = {"descuento": beca_data.descuento, "tipo": beca_data.tipo_descuento[0]};

        p_beca.innerText = `Beca: ${beca_data.nombre}`;
        p_beca.id = "estudiante-beca";
        if (estudiante.descuento) {
            p_beca.className = "mt-0";
        } else {
            p_beca.className = "mt-2";
        }
        
        document.querySelector("#div_id_estudiante").append(p_beca);

    } else {
        beca = false;

        if (document.querySelector("#estudiante-beca")) {
            document.querySelector("#estudiante-beca").innerText = "";
            document.querySelector("#estudiante-beca").className = "";
        }
    }

    calculo_precio();
}

function calculo_precio() {
    if (precio_clase) {
        
        let precio_final = precio_clase;        

        if (descuento) {
            precio_final -= descuento;

            if (precio_final<0) {precio_final=0}            
        }

        if (beca) {
            if (beca.tipo == "P") {
                precio_final = precio_final - (precio_final * beca.descuento) / 100;
            }

            if (beca.tipo == "C"){
                precio_final -= beca.descuento;
                if (precio_final<0) {precio_final=0}
            }
        }

        // Redondeo al entero mas cercano.
        precio_final = Math.round(precio_final);
        
        document.querySelector("#id_precio_a_pagar").value = precio_final;


        let p_final;

        if (document.querySelector("#precio-final")) {
            p_final = document.querySelector("#precio-final");
        } else {
            p_final = document.createElement("p");
        }
        
        p_final.innerText = `Precio Final Calculado = ${precio_final}$`;
        p_final.id = "precio-final";
        p_final.className = "mt-2";

        document.querySelector("#div_id_precio_a_pagar").append(p_final);


    } else {
        document.querySelector("#id_precio_a_pagar").value = "";
        document.querySelector("#precio-final").innerText = "";
    }
}


async function get_api_data(event, url) {

    let id = event.params.data.id;
    
    let csrf_token = document.querySelector("[name=csrfmiddlewaretoken]").value;
    
    let request = {
        method: "POST",
        headers: {'X-CSRFToken': csrf_token},
        mode: 'same-origin',
        body: JSON.stringify({"pk": id}),
    }
    
    
    try {
        let response = await fetch(url, request);
        let obj      = await response.json()
        
        return obj;    

    } catch (error) {
        console.error("Error al obtener los datos:", error);
        return {};
    }
}