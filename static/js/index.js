$("#procurar").click(function () {
    var url = $("#searchForm").attr("search");
    var input = $('#inputNumber').val();
    var tipo = $('#label_1').text();

    $.ajax({
        url: url,               
        data: {
            'parametro': input,
            'tipo': tipo
        },
        success: function (data) {
            label = '<label id="msg_erro_cpfcnpj" value="error" style="color:red">CPF/CNPJ Inválido</label>'
            if (data == label) {
                $("#msg_validar").html(data);
                $(".visivel").css('visibility', 'hidden')

            } else {
                $(".visivel").css('visibility', 'visible')
                $("#id_table").html(data);
                $("#msg_erro_cpfcnpj").remove();
            }
        }
    });
});

