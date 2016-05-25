var fechai = fechaf = ""
$.fn.dataTable.ext.search.push(
	function( settings, data, dataIndex ) {
		var min = fechai
		var max = fechaf
		var rango = data[2]

		if ( ( min == "" && max == "" ) ||
			 ( rango != 'No Bautizado' && min <= rango && max >= rango ) ||
			 ( rango != 'No Bautizado' && min <= rango && max <= rango )
		   )
		{
			return true;
		}

		return false;
	}
)

var fechaActual = ""
$.fn.dataTable.ext.search.push(
	function( settings, data, dataIndex ) {
		var dateA = fechaActual
		var dateB = data[2]
		var momentObj

		if( dateA && dateB != 'No Bautizado'){
			momentObj = moment(dateB)
			meses = dateA.diff(momentObj, 'months')
		}

		if ( ( dateA == "" ) || ( dateB != 'No Bautizado' && meses > 12 ) )
		{
			return true;
		}

		return false;
	}
)

var look = ""

$.fn.dataTable.ext.search.push(
	function( settings, data, dataIndex ) {
		var on = look
		var edad = data[1]

		if ( ( look == "" ) || ( on == 1 && edad > 18 ) || ( on == 2 && edad < 18 ) )
		{
			return true;
		}

		return false;
	}
)

function rgbToHex(rgb){
	rgb = rgb.match(/^rgba?[\s+]?\([\s+]?(\d+)[\s+]?,[\s+]?(\d+)[\s+]?,[\s+]?(\d+)[\s+]?/i);
	return (rgb && rgb.length === 4) ? "#" +
	("0" + parseInt(rgb[1],10).toString(16).toUpperCase()).slice(-2) +
	("0" + parseInt(rgb[2],10).toString(16).toUpperCase()).slice(-2) +
	("0" + parseInt(rgb[3],10).toString(16).toUpperCase()).slice(-2) : '';
}

jQuery.fn.dataTable.Api.register( 'rowColor()', function ( color ) {
    $.each(this.nodes(), function(key, node){
		colorRow = $(node).css('background-color')
		colorRow = rgbToHex(colorRow)

		if( colorRow === color){
			console.log(colorRow)
		}
	})

	/*$.fn.dataTable.ext.search.push(
		function( settings, searchData, index, rowData, counter ) {
			console.log(rowData)
			console.log(searchData)
			return true;
			return false;
		}
	);*/
})








