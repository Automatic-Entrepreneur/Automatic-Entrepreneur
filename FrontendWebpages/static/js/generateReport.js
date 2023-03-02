function generateReport(companyName) {
    $.ajax({
        type: "POST",
        url: "/report",
        async: false,
        data: { companyName: companyName },
        success: function(response) {
            document.location.href = "/" + response
        },
    });
}

$("#reportBtn").click(function(){
    generateReport($("#search").val());
});
