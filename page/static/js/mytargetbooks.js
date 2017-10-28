$(function () {
    $("#create_book_form").on("submit", function(){
        console.log('commit');
    });

    var deleteInfo = function(book_name){
        $("#modal-book").modal("show");
        html_sting = `\
        <div class="modal-header">\
        <button type="button" class="close" data-dismiss="modal" aria-label="Close">\
            <span aria-hidden="true">&times;</span>\
            </button>\
            <h4 class="modal-title">書本刪除</h4>\
        </div>\
        <div class="modal-body">\
            <p class="lead">已經從我的徵求書櫃刪除<strong>${book_name}</strong></p>\
        </div>\
        <div class="modal-footer">\
            <button type="button" class="btn btn-default" data-dismiss="modal">關閉</button>\
        </div>`;

        $("#modal-book .modal-content").html(html_sting);
    };

    // ask for target book info
    $('.show_target_info').click(function () {
        var button = this;
        $.ajax({
            'url': $(button).attr('href'),
            'type': 'GET'
        }).done(function (data) {
            $(button).siblings(".card-content").html(data.html_data);
        }).fail(function (e) {
            console.log(e);
        });
    });

    $('.btn-delete').click(function () {
        
        var button = this;
        $.ajax({
            'url': $(button).attr('href'),
            'type': 'DELETE'
        }).done(function () {
            $(button).parents('.book_item').remove();
            var book_name = $(button).parents(".book_item").children('.card-header').text();
            deleteInfo(book_name);
        }).fail(function (e) {
            console.log(e);
        });
    });
});