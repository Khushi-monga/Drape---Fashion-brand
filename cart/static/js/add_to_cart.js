document.addEventListener("DOMContentLoaded", () => {

    const form = document.getElementById("add-to-cart-form");

    if (!form) {
        return;
    }

    form.addEventListener("submit", async function (event) {

        event.preventDefault();

        const response = await fetch(
            form.action,
            {
                method: "POST",
                body: new FormData(form),
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            }
        );

        const data = await response.json();

        if (data.success) {

            const container =
                document.getElementById("cart-action");

            const cartUrl = container.dataset.cartUrl;

            container.innerHTML = `
                <a href="${cartUrl}">
                    <button type="button" class="btn-primary">
                        View Bag
                    </button>
                </a>
            `;
        }

    });

});