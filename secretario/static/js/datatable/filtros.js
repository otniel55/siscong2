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
