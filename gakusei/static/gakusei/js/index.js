document.addEventListener("DOMContentLoaded", function(){

    document.getElementById("solvencias-generate").onclick = e => solvencias_generate(e);
});

async function solvencias_generate(event){
    // console.log(event);
    
    // Definicion Variables
    let b = event.target;
    b.disabled = true;

    let i = document.getElementById("solvencias-i");
    let original_i_class = i.className;
    i.className = "fa-solid fa-spinner fa-spin-pulse";


    // Fetch
    let url = event.target.dataset.url;

    let response = await fetch(url);
    let obj      = await response.json();
    
    toastShow(obj.mensaje, obj.status);


    // Re-enable
    i.className = original_i_class;
    b.disabled = false;      
}


function toastShow(mensaje, status=true){

    const toast = document.getElementById('liveToast');
    let status_ok_class     = "toast align-items-center text-bg-success border-0";
    let status_not_ok_class = "toast align-items-center text-bg-danger border-0";


    if(status){
        toast.className = status_ok_class;
    } else {
        toast.className = status_not_ok_class;
    }

    document.getElementById('toast-text').innerText = mensaje;


    // Genera el Toast y lo muestra
    const toastBootstrap = bootstrap.Toast.getOrCreateInstance(toast);
    toastBootstrap.show();
}
