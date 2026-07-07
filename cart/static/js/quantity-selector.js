class QuantitySelector {

    constructor(element) {

        this.element = element;

        this.productId = element.dataset.productId;
        this.updateUrl = element.dataset.updateUrl;

        this.input = element.querySelector(".qty-input");
        this.plusBtn = element.querySelector(".qty-plus");
        this.minusBtn = element.querySelector(".qty-minus");

        this.csrfToken = getCookie("csrftoken");

        this.isSyncing = false;

        this.previousValue = Number(this.input.value);

        this.syncDebounced = debounce(
            () => this.sync(),
            800
        );

        this.registerEvents();

    }


    registerEvents() {

        this.plusBtn.addEventListener("click", () => {

            this.increment();

        });

        this.minusBtn.addEventListener("click", () => {

            this.decrement();

        });

        this.input.addEventListener("input", () => {

            this.validateInput();

            this.syncDebounced();

        });

    }


    increment() {

        this.input.value = Number(this.input.value) + 1;

        this.syncDebounced();

    }


    decrement() {

        const value = Number(this.input.value);

        if (value > 1) {

            this.input.value = value - 1;

            this.syncDebounced();

            return;

        }

        const form = this.element
            .closest(".cart-item")
            .querySelector(".remove-form");

        openRemoveModal(
            form,
            this.element.dataset.productName
        );

    }


    validateInput() {

        let value = parseInt(this.input.value);

        if (isNaN(value) || value < 1) {

            this.input.value = 1;

        }

    }


    setLoading(isLoading) {

        this.plusBtn.disabled = isLoading;
        this.minusBtn.disabled = isLoading;
        this.input.disabled = isLoading;

    }


    async sync() {

        if (this.isSyncing) {

            return;

        }

        this.isSyncing = true;

        this.setLoading(true);

        try {

            const response = await fetch(
                this.updateUrl,
                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/x-www-form-urlencoded",

                        "X-CSRFToken":
                            this.csrfToken,

                    },

                    body: new URLSearchParams({

                        product_id: this.productId,
                        quantity: this.input.value,

                    }),

                }
            );

            const data = await response.json();

            if (!data.success) {

                throw new Error(data.message);

            }

            this.input.value = data.quantity;

            this.previousValue = data.quantity;

            const itemSubtotal = document.getElementById(
                `item-subtotal-${this.productId}`
            );

            if (itemSubtotal) {

                itemSubtotal.textContent = `₹${data.item_subtotal}`;

            }

            const cartSubtotal = document.getElementById(
                "cart-subtotal"
            );

            if (cartSubtotal) {

                cartSubtotal.textContent = `₹${data.cart_subtotal}`;

            }

            const cartTotal = document.getElementById(
                "cart-total"
            );

            if (cartTotal) {

                cartTotal.textContent = `₹${data.cart_subtotal}`;

            }

            const cartCount = document.getElementById(
                "cart-count"
            );

            if (cartCount) {

                cartCount.textContent = data.cart_items;

            }

            document.dispatchEvent(

                new CustomEvent(

                    "cartUpdated",

                    {

                        detail: data

                    }

                )

            );

        }

        catch (error) {

            console.error(error);

            this.input.value = this.previousValue;

            alert("Unable to update cart.");

        }

        finally {

            this.isSyncing = false;

            this.setLoading(false);

        }

    }

}


document
    .querySelectorAll(".quantity-selector")
    .forEach(element => {

        new QuantitySelector(element);

    });