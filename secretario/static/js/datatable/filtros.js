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

		if ( ( look == "" ) || ( on == 1 && edad < 18 ) || ( on == 2 && edad > 18 ) )
		{
			return true;
		}

		return false;
	}
)


jQuery.fn.dataTable.Api.register( 'rowColor()', function ( color ) {
	function rgbToHex(rgb){
		rgb = rgb.match(/^rgba?[\s+]?\([\s+]?(\d+)[\s+]?,[\s+]?(\d+)[\s+]?,[\s+]?(\d+)[\s+]?/i);
		return (rgb && rgb.length === 4) ? "#" +
		("0" + parseInt(rgb[1],10).toString(16).toUpperCase()).slice(-2) +
		("0" + parseInt(rgb[2],10).toString(16).toUpperCase()).slice(-2) +
		("0" + parseInt(rgb[3],10).toString(16).toUpperCase()).slice(-2) : '';
	}

	var _settings = this.rows().settings()[0];
	var _rows = _settings.aoData

	$.each(_rows, function(key, row){
		colorRow = rgbToHex( row.anCells[4].style.backgroundColor )
		str = row._sFilterRow
		ubicacion = str.search('Estado')
		stringFilter = str.substring(0, ubicacion-1)
		stringFilter = stringFilter + " " + colorRow
		row._sFilterRow = stringFilter
	})

	this.draw()
})

jQuery.fn.dataTable.Api.register( 'searchColor()', function ( color ) {
	this.search( color ).draw()
})






