function getCookie(name) {

    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {

        const cookies = document.cookie.split(";");

        for (let cookie of cookies) {

            cookie = cookie.trim();

            if (cookie.startsWith(name + "=")) {

                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );

                break;

            }

        }

    }

    return cookieValue;

}


function debounce(callback, delay) {

    let timer;

    return (...args) => {

        clearTimeout(timer);

        timer = setTimeout(() => {

            callback(...args);

        }, delay);

    };

}


// ================= REMOVE MODAL =================

function attachRemoveModal() {

    const modal = document.getElementById("remove-modal");

    if (!modal) {
        return;
    }

    const productName = document.getElementById("modal-product-name");
    const confirmBtn = document.getElementById("confirm-remove");
    const cancelBtn = document.getElementById("cancel-remove");
    const closeBtn = document.getElementById("close-remove-modal");

    if (
        !productName ||
        !confirmBtn ||
        !cancelBtn ||
        !closeBtn
    ) {
        return;
    }

    let currentForm = null;

    function closeModal() {

        modal.classList.add("hidden");

        currentForm = null;

    }

    function openRemoveModal(form, name) {

        currentForm = form;

        productName.textContent = name;

        modal.classList.remove("hidden");

    }

    window.openRemoveModal = openRemoveModal;

    document.querySelectorAll(".open-remove-modal").forEach(button => {

        button.addEventListener("click", () => {

            openRemoveModal(
                button.closest("form"),
                button.dataset.productName
            );

        });

    });

    confirmBtn.addEventListener("click", () => {

        if (!currentForm) {
            return;
        }

        currentForm.submit();

    });

    cancelBtn.addEventListener("click", closeModal);

    closeBtn.addEventListener("click", closeModal);

    modal.addEventListener("click", event => {

        if (event.target === modal) {

            closeModal();

        }

    });

}


document.addEventListener("DOMContentLoaded", () => {

    attachRemoveModal();

});