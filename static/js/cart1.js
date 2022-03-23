<script>


function add_to_cart(pid, pname, price, category, image) {

    let cart = localStorage.getItem("cart");
    if (cart == null) {
        //no cart yet
        let products = [];
        let product = {
            productId: pid, productName: pname, productQuantity: 1, productPrice: price, productCategory: category,
            productImage: image
        };
        products.push(product);
        localStorage.setItem('cart', JSON.stringify(products));
        console.log('Product Added')

    } else {
        // cart is already present
        let pcart = JSON.parse(cart);

        let oldProduct = pcart.find((item) => item.productId == pid)
        if (oldProduct) {
            alert("Product Already Added!");
            console.log('Product already added')
            //quantity
        } else {
            //product
            let product = {
                productId: pid, productName: pname, productQuantity: 1, productPrice: price, productCategory: category,
                productImage: image
            };
            pcart.push(product);
            localStorage.setItem('cart', JSON.stringify(pcart));
            console.log('Product Quantity Added')

        }
    }
    updateCart();

}

// cart Update
function updateCart() {
    let cartString = localStorage.getItem("cart");
    let cart = JSON.parse(cartString);
    if (cart == null || cart.length == 0) {
        console.log("Cart is Empty")
        $(".cart-items").html("(0)");
        $(".cart-body").html("<h3>Cart does not have any items</h3>");
        $(".checkout-btn").addClass('disabled');

    }
    else {
        //thre is something
        console.log(cart.length)

        $(".cart-items").html(`(${cart.length})`);
        let table = `
    <table class='table'>
        <thead class='thead-light'>
            <tr>
                <th>Picture</th>
                <th>Item Name</th>
                <th>Item price</th>
                <th>Item Quantity</th>
                <th>Total Price</th>
                <th>Action</th>
    
            </tr>
    
        </thead>
    
        `

        let totalPrice = 0;



        cart.map((item) => {

            table += `
        <tr>
            <td>
                
            <img class="card" style="height:100px; width:100px;" src="/static/image/product/${item.productCategory}/${item.productImage}" alt="hello">
            </td>
    
            <td>
                ${item.productName}<br><br>${item.productCategory}
            </td>
    
    
            <td>
                <div id="price">${item.productPrice}</div>
            </td>
    
    
            <td>
                <div class="chevrons">
                    <button class="btn btn-sm" value="${item.productId}" onclick="increment(this.value)"><i class="fas fa-chevron-up"></i></button>
                    <span class="item-amount quan_y" id="quantity" name="quantity" value="${item.productQuantity}">${item.productQuantity}</span>
                    <button class="btn btn-sm" value="${item.productId}" onclick="decrement(this.value)"><i class="fas fa-chevron-down"></i></button>
                </div>

             
            </td>
    
    
            <td>
    
                <div class="totalP">${item.productPrice * item.productQuantity}</div>
            </td>
    
            <td>
                <button value="${item.productId}" id="button" onclick="removeProduct(this.value)" class="btn btn-danger btn-sm">
                    Remove
                </button>
            </td>
    
    
        </tr>
    
    
    
        `;
            totalPrice += item.productPrice * item.productQuantity;


        })

        table = table +
            `
        <tr>
            <td colspan='5' class='text-right'>
                Total Price: ${totalPrice}
            </td>
        </tr>
    </table>
    `
        $(".cart-body").html(table);


    }
    $(document).ready(function () {

    });

}
//gist.github.com/umutyerebakmaz/fa824be8196bad0bce3b002e2d741617 
function removeProduct(value) {

    let cartString = localStorage.getItem("cart");
    let cart = JSON.parse(cartString);
    cart = cart.filter(item => item.productId !== value);
    localStorage.setItem('cart', JSON.stringify(cart));
    console.log('Product removed')
    updateCart();

}

function increment(value) {
    let cartString = localStorage.getItem("cart");
    let pcart = JSON.parse(cartString);

    let oldProduct = pcart.find((item) => item.productId == value)
    if (oldProduct.productQuantity >= 5) {
        $(this.button).addClass('disabled');
    } else {
        oldProduct.productQuantity = oldProduct.productQuantity + 1
        pcart.map((item) => {
            if (item.productId == oldProduct.productId) {
                item.productQuantity = oldProduct.productQuantity;
            }
        })
        localStorage.setItem('cart', JSON.stringify(pcart));
        console.log(' Quantity increased')
    }

    updateCart()
}

function decrement(value) {
    let cartString = localStorage.getItem("cart");
    let pcart = JSON.parse(cartString);

    let oldProduct = pcart.find((item) => item.productId == value)
    if (oldProduct.productQuantity <= 1) {
        $(this.button).addClass('disabled');
    } else {
        oldProduct.productQuantity = oldProduct.productQuantity - 1
        pcart.map((item) => {
            if (item.productId == oldProduct.productId) {
                item.productQuantity = oldProduct.productQuantity;
            }
        })
        localStorage.setItem('cart', JSON.stringify(pcart));
        console.log('Product Quantity decresed')
    }

    updateCart()

}

$(document).ready(function () {
    updateCart();
});
</script>