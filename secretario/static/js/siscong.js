function Gestion(){
    var _inputs
    var _tables
    var _json

    this.getInputs = function(elemento){

        Clear = 0
        Data = []

        inputs = $(':text, :password, select, input[type="number"], input[type="email"]', ''+elemento)

        inputs.each(function(){
            vacio=false
            $(this).css('border-color', '#ccc')

            if( !$(this).val() ){
                vacio=true
            } else {
                if ($(this).attr("type")=="number"){
                    if( !/^([0-9])*$/.test( $(this).val() ) ){
                        vacio=true
                    }
                }
            }
            if (vacio){
                $(this).css('border-color', 'red')
                Clear++
            }else{
                Data.push({
                    'value' : $(this).val()
                })
            }
        })

        this._inputs = {
                'Data': Data,
                'vacio': Clear
                }

        return this._inputs
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

        if(this._inputs){
            json = {}

            if(adicional){
                if ( !Array.isArray(adicional) ){
                    this._inputs.Data.push({ 'value' : adicional })
                } else {
                    $.each(adicional, function(key, value){
                        this._inputs.Data.push({ 'value' : value })
                    })
                }
            }

            keys.push('csrfmiddlewaretoken')
            this._inputs.Data.push({ 'value' : csrf })

            $.each(this._inputs.Data, function(key, value){
                json[keys[key]] = value.value
            })

            this._json = json
            return this._json
        }

    }

    this.setPost = function(url, titulo, func){

        $.post(url, this._json)
        .success(function(res){
			if (titulo){
				res = JSON.parse(res)
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
						func()
					}
				}
			}else{
				func()
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
