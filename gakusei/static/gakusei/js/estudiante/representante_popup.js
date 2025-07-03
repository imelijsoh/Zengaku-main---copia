document.addEventListener("DOMContentLoaded", function() {

    document.querySelector("#representante-form").addEventListener("submit", function(event) {

        event.preventDefault();

        let form = event.target;
        let form_data = new FormData(form);

        let status;
        let id;
        let form_error;

        fetch(form.action, {
            method: form.method,
            body: form_data
        })
        .then(r => {
            status = r.ok;
            return r.json()
        })
        .then(response => {
            if (status) {
                console.log(response);
                
                id = response.id;
            } else {
                form_error = response.error_form;
            }
        })
        .finally(() => {
            if (status) {
                if (window.opener && typeof window.opener.recibirRepresentante === 'function') {
                    window.opener.recibirRepresentante(id);

                    window.close();
                }
            } else {
                document.querySelector("#representante-form-fields").innerHTML = form_error;
            }
        });

    });



});