var vm = new Vue({
    el: '#app',
	// 修改Vue变量的读取语法，避免和django模板语法冲突
    delimiters: ['[[', ']]'],
    data: {
        host: host,
        order_submitting: false, // 正在提交订单标志
        pay_method: 2, // 支付方式,默认支付宝支付
        nowsite: '', // 默认地址
        payment_amount: '',
    },
    mounted(){
        // 初始化
        this.payment_amount = payment_amount;
        // 绑定默认地址
        this.nowsite = default_address_id;
    },
    methods: {
        // 提交订单
        on_order_submit(){
            if (!this.nowsite) {
                alert('请补充收货地址');
                return;
            }
            if (!this.pay_method) {
                alert('请选择付款方式');
                return;
            }
            if (this.order_submitting == false){
                this.order_submitting = true;
                var url = this.host + '/orders/commit/';

                // 回想一下，利用HTTP协议向服务器传参有几种途径？
                // 拼接在url后特定部分,可以在服务器端的路由中用正则表达式截取:如/weather/beijing/2018
                // 拼接在url后查询字符串（query string)形式，形如key1=value1&key2=value2；
                // 请求体（body）中发送的数据，比如表单数据、json、xml；
                // 在http报文的头（header）中。

                axios.post(url, {
                        address_id: this.nowsite,
                        pay_method: this.pay_method
                    }, {
                        headers:{
                            'X-CSRFToken':getCookie('csrftoken')
                        },
                        responseType: 'json'
                    })
                    .then(response => {
                        if (response.data.code == '0') {
                            location.href = '/orders/success/?order_id='+response.data.order_id
                                        +'&payment_amount='+this.payment_amount
                                        +'&pay_method='+this.pay_method;
                        } else if (response.data.code == '4101') {
                            location.href = '/login/?next=/orders/settlement/';
                        } else {
                            alert(response.data.errmsg);
                        }
                    })
                    .catch(error => {
                        this.order_submitting = false;
                        console.log(error.response);
                    })
            }
        }
    }
});
