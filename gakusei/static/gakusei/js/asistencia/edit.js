document.addEventListener("DOMContentLoaded", function(){

    document.querySelector("#asistencia-form").addEventListener("submit", () => {

        document.querySelector("#id_dia_clase").disabled  = false;
        document.querySelector("#id_estudiante").disabled = false;
        // alert("a");
    });
    

});
