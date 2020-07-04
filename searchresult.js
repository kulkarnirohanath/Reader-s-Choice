<script src="https://code.jquery.com/jquery-latest.min.js"></script>

$(document).ready(function(){
  function asynch()
  {
    var searchname_data = $('#searchname').val();
    var searchby_data = $('#searchby').val();
    $('#search').onclick(function(){
      $.ajax({
        url: "/search",
        type: "post",
        data: { searchby: searchby_data, searchname: searchname_data }
        success: function(response) {
          $("#place_for_table").html(response)
        },
        error: function() {
          $("#place_for_table").html("Data not available")
        }
      });
    });
  }
});
