
// NOTE: keep sync'd with prices on the server @ app/utils/invoice.py
// (which are actually used to create invoice)
const providers = {
    'digital_ocean': { 'price_per_month': 10.00, 'currency': 'USD' }
}

$( document ).ready(function() {
    const update_price = function() {
        const monthsToAdopt = Number($('.js-months').val());
        const provider = $('.js-provider').val();

        if (providers[provider] && Number.isInteger(monthsToAdopt)) {
            price = providers[provider]['price_per_month'] * monthsToAdopt
            priceString = "$" + price.toFixed(2);
            $('.js-price').text(priceString);
        }

        return
    }

    $(".js-months").on("change paste keyup", function() {
        update_price()
    });

    $(".js-provider").on("click change", function() {
        update_price()
    });
});
