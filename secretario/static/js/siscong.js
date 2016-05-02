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

	//objeto
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

	//funciones del sistema
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

	function crearTablePie(results, index){
		exclude = ['torta', 'mes', 'result', 't']
		labels = ['tPubs', 'tBau', 'tIrreg', 'tAux', 'tReg']
		labels2 = ['pubs', 'bau', 'irreg', 'aux', 'reg']

		$('#tDetail tbody').html("")

		json = orderByKey(results[index])

		//creando las filas y las 2 primeras columnas
		$.each(json, function(key, value){
			if(exclude.indexOf(key) == -1){
				if(labels2.indexOf(key) == -1){
					key = toUpperFirst(key)
				} else {
					key = labels2.indexOf(key)
					switch(key){
						case 0:
							key = 'Publicadores'
						break
						case 1:
							key = 'Bautizados'
						break
						case 2:
							key = 'Irregulares'
						break
						case 3:
							key = 'Prec. Aux.'
						break
						case 4:
							key = 'Prec. Reg.'
						break
					}
				}

				$('#tDetail tbody').append(
					'<tr>\
						<td>'+key+'</td>\
						<td>'+value+'</td>\
					</tr>'
				)
			}
		})

		//agregando la columna con datos del mes anterior
		i=0
		if(index < Object.keys(results).length-1 &&  results[index+1].torta){
			json2 = orderByKey(results[index+1])
			$.each(json2, function(key, value){
				if(exclude.indexOf(key) == -1){
					$('#tDetail tbody tr:eq('+i+') td:nth-child(1)').after('<td>'+value+'</td>')
					i++
				}
			})
		} else {
			$.each(json, function(key, value){
				if(exclude.indexOf(key) == -1){
					$('#tDetail tbody tr:eq('+i+') td:nth-child(1)').after('<td>-</td>')
					i++
				}
			})
		}

		//agregando la columna con los % obtenidos
		i=0
		$.each(json.torta, function(key, value){
			if(exclude.indexOf(key[0]) == -1){
				$('#tDetail tbody tr:eq('+i+') td:nth-child(3)').after('<td>'+value+'</td>')
				i++
			}
		})
	}

	function createDoughnut(array, init){
		function __init__(key, array){
			if(array.torta){
				exclude = ['torta', 'mes', 'result', 't']
				labels = ['tPubs', 'tBau', 'tIrreg', 'tAux', 'tReg']
				labels2 = ['pubs', 'bau', 'irreg', 'aux', 'reg']

				//obteniendo el nro de segmentos a mostrar
				i=0
				torta={}
				nroT= 0
				$.each(array.torta, function(key, value){
					if(exclude.indexOf(key[0]) == 3){
						torta[key] = value
						nroT++
					}
				})

				//Eliminando o Agregando segmentos a la dona
				switch(key){
					case '0':
					case '3':
						removeSegmentsPie(pie3, nroT, pie3.segments.length)
					break

					case '1':
					case '4':
						removeSegmentsPie(pie2, nroT, pie2.segments.length)
					break

					case '2':
					case '5':
						removeSegmentsPie(pie1, nroT, pie1.segments.length)
					break
				}

				//llenando la dona con los valores t obtenidos
				i=0
				firstEachKey = key
				$.each(torta, function(key, value){

					if(labels.indexOf(key) == -1){
						label = key.substr(1)
					} else {
						label = labels.indexOf(key)
						switch(label){
							case 0:
								label = 'Publicadores'
							break
							case 1:
								label = 'Bautizados'
							break
							case 2:
								label = 'Irregulares'
							break
							case 3:
								label = 'Prec. Aux.'
							break
							case 4:
								label = 'Prec. Reg.'
							break
						}
					}

					data = {
						index: i,
						label: label,
						value: value
					}

					switch(firstEachKey){
						case '0':
						case '3':
							addValPie(pie3, data)
						break

						case '1':
						case '4':
							addValPie(pie2, data)
						break

						case '2':
						case '5':
							addValPie(pie1, data)
						break
					}
					i++
				})

				//creando la leyenda
				switch(key){
					case '0':
					case '3':
						pie3.update();
						createLegend('pie3', pie3)
						$('#pie3').siblings().children().removeClass('hide')
					break

					case '1':
					case '4':
						pie2.update();
						createLegend('pie2', pie2)
						$('#pie2').siblings().children().removeClass('hide')
					break

					case '2':
					case '5':
						pie1.update();
						createLegend('pie1', pie1)
						$('#pie1').siblings().children().removeClass('hide')
					break
				}

				$('label[for="pie'+labelPie+'"]').html('Distribucion del '+array.result+'% de '+mes)

				labelPie--
			} else {
				switch(key){
					case '0':
					case '3':
						initialDoughnut('pie3', pie3)
					break

					case '1':
					case '4':
						initialDoughnut('pie2', pie2)
					break

					case '2':
					case '5':
						initialDoughnut('pie1', pie1)
					break
				}
			}
		}

		labelPie = 3

		if(init){
			while(init < Object.keys(array).length ){
				$.each(array[init], function(key, value){
					__init__(key, value)
				})
				init++
			}
		} else {
			$.each(array, function(key, value){
				if(key < 3){
					__init__(key, value)
				}
			})
		}
	}
