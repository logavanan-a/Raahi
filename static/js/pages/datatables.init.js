
$(document).ready(function () {
    // Initialize the DataTable with options
    $("#datatable").DataTable({
        buttons: ["colvis"],
        stateSave: true,
        paging: true,
        searching: false, // Disable searching
        info: true,
        ordering: true,
        bRetrieve: true,
        responsive: false, // Disable responsive features, including the dtr-control button
        scrollX: true, // Set the height of the scrollable area, adjust as needed
        scrollCollapse: true // Enable scrollbar collapse
    }).buttons().container().appendTo("#datatable-buttons_wrapper .col-md-6:eq(0)");

    // Add a class to the length select dropdown for styling
    $(".dataTables_length select").addClass("form-select form-select-sm");
});

// "copy","excel","pdf","colvis"