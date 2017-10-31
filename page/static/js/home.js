$(function () {

    $(document).on('submit', '.search-form',function () {
        var form = $(this);

        $.ajax({
            'url': form.attr("action"),
            'data': form.serialize(),
            'type': 'GET'
        }).done(function (data) {
            if (data.is_valid) {
                $('.search-result').html(data.html_data)
            }
        }).fail(function (e) {
            console.log(e);
        });
        return false;
    });
});