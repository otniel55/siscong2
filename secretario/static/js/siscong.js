function Gestion(){
    var _datosIn
    var _inputs
    var _tables
    var _json

    this.Cargar = function(datos){

        this._inputs.each(function(key){
            $(this).css('border-color', '#ccc')
            if (datos){
                if ( !Array.isArray() ){
                    console.log($(this))
                    $(this).val(datos)
                }else{
                    $(this).val(datos[key])
                }
            }else{
                if( !$(this).is('select')){
                    $(this).val("")
            } else {
                if ( $(this).is('select') ){
                    $(this).find('option:first').prop('selected', true)
                }
            }
            }
        });
    }

    this.getInputs = function(elemento, intervalo){

        input = $(':text, :password, select, input[type="number"], input[type="email"]', ''+elemento)

        if(intervalo){
            if(Array.isArray(intervalo)){
                datos = []
                input.each(function(key, value){
                    if(key>=intervalo[0] && key<=intervalo[1]){
                        datos.push(value)
                    }
                })
                input = $(datos)
            } else {
                input = input.eq(intervalo)
            }
        }

        if( this._inputs ){
            if( Array.isArray(input) ){
                input.each(function(key, value){
                    this._inputs.push(value)
                })
            } else {
                this._inputs.push(input.eq(0))
            }
        } else {
            this._inputs = input
        }

        console.log(this._inputs)
    }

    this.getDataIn = function(){
        Clear = 0
        Data = []

        this._inputs.each(function(){
            vacio=false
            $(this).css('border-color', '#ccc')

            if( !$(this).val().trim() ){
                vacio=true
            } else {
                if ( $(this).is('[type="number"]') ){
                    if( !/^([0-9])*$/.test( $(this).val() ) ){
                        vacio=true
                    }
                }
            }
            if (vacio){
                $(this).css('border-color', '#d90000')
                Clear++
            }else{
                Data.push({
                    'value' : $(this).val()
                })
            }
        })

        this._datosIn = {
                'Data': Data,
                'vacio': Clear
                }
        console.log(this._datosIn)
        return this._datosIn
    }

    this.getDataTable = function(table){

        if( !Array.isArray(table) ){

            this._tables = {
                nodes : table.rows().nodes(),
                Data : table.rows().data()
            }

        } else {
            tables = []
            $.each(table, function(key, value){
                tables.push({
                    nodes: value.rows().nodes(),
                    data: value.rows().data()
                })
            })
            this._tables = tables
        }

        return this._tables
    }

    this.generateJson = function(keys, csrf, adicional){

        if(this._datosIn){
            json = {}

            if(adicional){
                if ( !Array.isArray(adicional) ){
                    this._datosIn.Data.push({ 'value' : adicional })
                } else {
                    $.each(adicional, function(key, value){
                        this._datosIn.Data.push({ 'value' : value })
                    })
                }
            }

            keys.push('csrfmiddlewaretoken')
            this._datosIn.Data.push({ 'value' : csrf })

            $.each(this._datosIn.Data, function(key, value){
                json[keys[key]] = value.value
            })

            this._json = json

            console.log(this._json)
            return this._json
        }

    }

    this.setPost = function(url, titulo, func){

        $.post(url, this._json)
        .success(function(res){
            res = JSON.parse(res)

			if (titulo){
				$.gritter.add({
					title: titulo,
					text: ''+res.msg,
					image: '',
					sticky: false,
					time: 3000,
					class_name: ''
				});
				if(func){
					if (res.on==1){
						func(res)
					}
				}
			} else {
				func(res)
			}
        })
    }

    this.ejecutarLoad = function(url, div){
        if( div.is(':hidden') ){
            div.load(url, function(){
                div.show( 'blind', 1000 );
            });
        } else {
            div.hide('blind', 1000, function(){
                div.load(url, function(){
                    div.show( 'blind', 1000 );
                });
            })
        }
    }
}

    function createPager(tabla, nro){

        filas = tabla.data().length

        if($('#pager'+nro).children().length > 2){
            $('#pager'+nro).children().each(function(){
                if( !$(this).is(':first-child') && !$(this).is(':last-child')){
                    $(this).detach()
                }
            })
        }

        if(filas > 10){
            page = 1
            index = 0
            while(filas>0){
                filas = filas - 10

                $('#pager'+nro+' > li:eq('+index+')').after(
                    '<li><a href="#" aria-label="'+index+'">'+page+'</a></li>'
                )

                index++
                page++
            }

            if( $('#pager'+nro).is(':hidden') ){
                $('#pager'+nro).removeClass('hide')
                $('#pager'+nro).show().children().show()
            }

            $('nav.center-block:eq('+(nro-1)+')').width( $('#pager'+nro).width() )

            $('#pager'+nro+' > li > a').click(function(){
                val = $(this).attr('aria-label')

                if(val === 'N'){
                    tabla.page( 'next' ).draw( 'page' );
                } else if (val === 'P'){
                    tabla.page( 'previous' ).draw( 'page' );
                } else {
                    val = parseInt(val)
                    tabla.page( val ).draw( 'page' );
                }

                reajustarTables()
            })

            return 1

        } else {
            if( $('#pager'+nro).is(':visible') )
                $('#pager'+nro).hide()

            return 0
        }
    }

    function reajustarTables(alto){
        if( !alto ){
            alto1 = $('#tabla1')[0].clientHeight
            alto2 = $('#tabla2')[0].clientHeight
        } else {
            alto1 = alto2 = alto
        }

        if(alto1 >= alto2){
            $('div.content-panel').height(alto1+'px')
        } else {
            $('div.content-panel').height(alto2+'px')
        }
    }

    function changeStateInput(hermano, value, cmb){
        if(value == 3 || value == 4){
            hermano.children().detach()
            hermano.append('<input type="number" min=0 placeholder="Nro de Precursor" class="form-control" />')
        } else if ( value ){
            if ( hermano.children().is('input') ){
                hermano.children().detach()
                hermano.append(cmb).children().removeAttr('disabled')
            } else {
                if(hermano.children().is(':disabled'))
                    hermano.children().removeAttr('disabled')
            }
        } else {
            hermano.children().attr('disabled', true)
        }
    }

	function createLegend(id, dona){
		helpers = Chart.helpers;
		legend = $('#'+id).parent().siblings()
		legend.html( dona.generateLegend() )

		helpers.each(legend.children().children(), function(legendNode, index){
			helpers.addEvent(legendNode.firstChild , 'mouseover', function(){
				activeSegment = dona.segments[index]
				activeSegment.fillColor = activeSegment.highlightColor;
				dona.showTooltip([activeSegment])
				legendNode.style.backgroundColor = 'rgba(209, 215, 217, 0.69)'
			})

			helpers.addEvent(legendNode.firstChild, 'mouseout', function(){
				dona.draw();
				legendNode.removeAttribute('style')
			})
		})
	}

	function toUpperFirst(string){
		string = string.substr(0, 1).toUpperCase() + string.substr(1).toLowerCase();
		return string
	}

	function randomColor() {
		return 'rgb(' + Math.round(Math.random() * 255) + ',' + Math.round(Math.random() * 255) + ',' + Math.round(Math.random() * 255) + ')'
	};

	function addValPie(pie, data){
		pie.segments[data.index].value = data.value
		pie.segments[data.index].label = data.label
	}

	function removeSegmentsPie(pie, sgValT, sgTotal){
		if(sgValT < sgTotal){
			for(i=sgValT;i<sgTotal;i++){
				pie.removeData()
			}
		} else {
			for(i=sgTotal;i<sgValT;i++){
				color = randomColor()
				pie.addData({
					value: 0,
					color: color,
					highlight: color,
					label: ""
				})
			}
		}
	}

	function orderByKey(array){

		keys = Object.keys(array.torta)
		keys.sort();

		jsonOrder = {}

		for(j=0;j<keys.length;j++){
			x = keys[j]
			jsonOrder[x] = array.torta[x]
		}
		array.torta = jsonOrder

		keys = Object.keys(array)
		keys.sort();

		jsonOrder = {}

		for(j=0;j<keys.length;j++){
			x = keys[j]
			jsonOrder[keys[j]] = array[x]
		}

		return jsonOrder
	}

	function initialDoughnut(id, dona){
		$('#'+id).parent().siblings(':eq(0)').children().detach()
		$('#'+id).siblings().children().addClass('hide')
		$('label[for="'+id+'"]').html("")

		$.each(dona.segments, function(key, value){
			value.value = 0
		})
		dona.update()
	}

    $(document).ready(function(){

        $('.datepicker').datetimepicker({
            format: 'MM-YYYY',
            widgetPositioning:  {
              horizontal: 'right',
              vertical: 'auto',
            },
            maxDate:'now'
        })

        $( ".datepicker2" ).datetimepicker({
            showTodayButton:true,
            viewMode: 'days',
            format: 'YYYY-MM-DD',
            widgetPositioning: {
                horizontal: 'right',
                vertical: 'auto'
            },
            maxDate: 'now'
        })
    })
