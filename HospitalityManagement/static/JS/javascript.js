function addComment(roomId) {
    let content = document.getElementById('commentId')
    if(content !== null) {
        fetch('/api/comments', {
            method: 'post',
            body: JSON.stringify ({
                'room_id': roomId,
                'content': content.value
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(res => res.json()).then(data => {
            if(data.status == 201) {
                let c = data.comment

                let area = document.getElementById('commentArea')

                area.innerHTML = `
                    <div class="row">
                        <div class="col-md-1 col-xs-4">
                            <img class="img-fluid rounded-circle" src="${c.user.avatar}" alt="avatar" />
                        </div>

                        <div class="col-md-11 col-xs-8">
                            <p>${c.content}</p>
                            <p><em>${moment(c.created_date).locale('vi').fromNow()}</em></p>
                        </div>
                    </div>
                ` + area.innerHTML //chèn cmt mới lên đầu
            } else if(data.status == 404)
                alert(data.err_msg)
    })
    }
}


function addToCart(id, name, price) {
    event.preventDefault()


    const checkinDate = document.getElementById(`checkin_date`)
    const checkoutDate = document.getElementById(`checkout_date`)

    if (!checkinDate.value || !checkoutDate.value) {
        alert('Vui lòng chọn cả ngày nhận và ngày trả trước khi thêm vào giỏ hàng.');
        return;
    }

    fetch('/api/add-cart', {
        method: 'post',
        body: JSON.stringify({
            'id': id,
            'name': name,
            'price': price,
            'checkinDate': checkinDate.value,
            'checkoutDate': checkoutDate.value
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(function(res) {
        if(res.ok){
            $('#myModal').modal('show');
            return res.json()
        }
        else
            alert('Ngày nhận phòng không vượt quá 28 ngày kể từ ngày đặt và ngày nhận phòng phải nhỏ hơn ngày trả phòng');
    }).then(function(data) {
        console.info(data)

        let counter = document.getElementsByClassName('cart-counter')
        for (let i = 0; i < counter.length; i++)
            counter[i].innerText = data.total_quantity
    }).catch(function(err) {
        console.error(err)
    })
}


function updateCart(id, obj){
    fetch('/api/update-cart', {
        method: 'put',
        body: JSON.stringify ({
            'id': id,
            'quantity': parseInt(obj.value)
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(res => res.json()).then(data => {
        let counter = document.getElementsByClassName('cart-counter')
        for (let i = 0; i < counter.length; i++)
            counter[i].innerText = data.total_quantity

        let amount = document.getElementById('total-amount')
        amount.innerText = new Intl.NumberFormat().format(data.total_amount)
    })
}

function deleteCart(id) {
    if (confirm('Bạn có chắc chắn muốn bỏ chọn phòng này không??') == true) {
        fetch('/api/delete-cart/' + id, {
            method: 'delete',
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(res => res.json()).then(data => {
            let counter = document.getElementsByClassName('cart-counter')
            for (let i = 0; i < counter.length; i++)
                counter[i].innerText = data.total_quantity

            let amount = document.getElementById('total-amount')
            amount.innerText = new Intl.NumberFormat().format(data.total_amount)

            let e = document.getElementById('room' + id)
            e.style.display = "none"
        }).catch(err => console.error(err))
    }
}

function reservation() {
    if (confirm('Bạn có chắc chắn muốn xác nhận đặt phòng??') == true) {
        fetch('/api/reservation', {
            method: 'post'
        }).then(res => res.json()).then(data => {
            if (data.code == 200)
                location.reload()
        }).catch(err => console.error(err))
    }
}
