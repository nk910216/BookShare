$(function () {

    var messageInfo = function(message){
        $("#modal-exchange").modal("show");
        html_string = `\
        <div class="modal-header">\
        <button type="button" class="close" data-dismiss="modal" aria-label="Close">\
            <span aria-hidden="true">&times;</span>\
            </button>\
            <h4 class="modal-title">通知</h4>\
        </div>\
        <div class="modal-body">\
            <p class="lead"><strong>${message}</strong></p>\
        </div>\
        <div class="modal-footer">\
            <button type="button" class="btn btn-default" data-dismiss="modal">關閉</button>\
        </div>`;
        $("#modal-exchange .modal-content").html(html_string);
    };

    // regret
    $('.exchange-regret').click(function () {
        var button = this;
        $.ajax({
            'url': $(button).attr('href'),
            'type': 'POST'
        }).done(function (data) {
            messageInfo(data.message)
            if (data.is_valid) {
                $(button).parents('.waiting_exchange').remove();
            }
        }).fail(function (e) {
            console.log(e);
        });
    });

    // reject
    $('.exchange-reject').click(function () {
        var button = this;
        $.ajax({
            'url': $(button).attr('href'),
            'type': 'POST'
        }).done(function (data) {
            messageInfo(data.message)
            if (data.is_valid) {
                $(button).parents('.deciding_exchange').remove();
            }
        }).fail(function (e) {
            console.log(e);
        });
    });

    // reject noticed
    $('.exchange-reject-noticed').click(function () {
        var button = this;
        $.ajax({
            'url': $(button).attr('href'),
            'type': 'POST'
        }).done(function (data) {
            messageInfo(data.message)
            if (data.is_valid) {
                $(button).parents('.rejected_exchange').remove();
            }
        }).fail(function (e) {
            console.log(e);
        });
    });

    // target book deleted
    $('.exchange-book-deleted').click(function () {
        var button = this;
        $.ajax({
            'url': $(button).attr('href'),
            'type': 'POST'
        }).done(function (data) {
            messageInfo(data.message)
            if (data.is_valid) {
                $(button).parents('.target_delete_noticed').remove();
            }
        }).fail(function (e) {
            console.log(e);
        });
    });

    // cnofirm
    $('.exchange-confirm').click(function () {
        var button = this;
        $.ajax({
            'url': $(button).attr('href'),
            'type': 'POST'
        }).done(function (data) {
            messageInfo(data.message)
            if (data.is_valid) {
                $(button).parents('.deciding_exchange').remove();
                $('.confirm_none_message').hide();
                $('.exchange_confirmed_block').prepend(data.html_data);
            }
        }).fail(function (e) {
            console.log(e);
        });
    });

    // cnofirm source notice.
    $('.exchange_confirm_source_noticed').click(function () {
        var button = this;
        $.ajax({
            'url': $(button).attr('href'),
            'type': 'POST'
        }).done(function (data) {
            messageInfo(data.message)
            if (data.is_valid) {
                $(button).parents('.source_confirm_exchange').remove();
            }
        }).fail(function (e) {
            console.log(e);
        });
    });

    // cnofirm target notice.
    $(document).on('click', '.exchange_confirm_target_noticed',function () {
        var button = this;
        $.ajax({
            'url': $(button).attr('href'),
            'type': 'POST'
        }).done(function (data) {
            messageInfo(data.message)
            if (data.is_valid) {
                $(button).parents('.target_confirm_exchange').remove();
            }
        }).fail(function (e) {
            console.log(e);
        });
    });
});