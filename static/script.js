 // Javascript toggle blur & popup script (books.html/members.html)
 function toggle(){
    var blur = document.getElementById('blur');
    blur.classList.toggle('active');
    var popup = document.getElementById('popup');
    popup.classList.toggle('active');
}


// Populate popup form fields with corresponding values of a selected book (books.html)
function editBook(id, title, author, genre, year, stock){
    document.getElementById("form_id").value = id;
    document.getElementById("form_title").value = title;
    document.getElementById("form_author").value = author;
    document.getElementById("form_genre").value = genre;
    document.getElementById("form_year").value = year;
    document.getElementById("form_stock").value = stock;
}


// Dynamic search with AJAX and jQuery (books.html)
function searchBook() {
    var query = $('#search').val();
    var field = $('#field').val();
    $.get('/books', {'query': query, 'field': field}, function(data) {
        var table = $('#books tbody');
        table.empty();
        if (query === '') {  // If query empty
            window.location.reload();  // Reload template
        } else {
            data.forEach(function(book) {
                var row = $('<tr></tr>');
                row.append($('<td></td>').text(book.id));
                row.append($('<td></td>').text(book.title));
                row.append($('<td></td>').text(book.author));
                row.append($('<td></td>').text(book.genre));
                row.append($('<td></td>').text(book.year));
                row.append($('<td></td>').text(book.stock));
                
                form = $('<form></form>').attr('action', '/books').attr('method', 'POST').on('click', function(e) {
                    if (!confirm('Completely remove \'' + book.title + '\' by ' + book.author + ' (book ID: ' + book.id + ') and all of its stock from library database?')) {
                        e.preventDefault();  // Prevent form submission if user cancels
                    }
                });
                input = $('<input>').attr("name", 'id').attr('value', book.id).hide()
                button = $('<button></button>').text('Remove').addClass('button').attr('name', 'button').attr('value','remove');

                form.append(input).append(button);  // Input & button inside form element
                
                row.append($('<td></td>').append(form));
                row.append($('<td></td>').append($('<button></button>').text('Edit').addClass('button btn-edit').click(function() {
                    toggle();
                    editBook(book.id, book.title, book.author, book.genre, book.year, book.stock);
                })));   // Toggle and editForm functions appended along with Edit button class
                table.append(row);
            });
        }
    });
}


// Dynamic search with AJAX and jQuery (catalogue.html)
function searchCatalogue() {
    var query = $('#search').val();
    var field = $('#field').val();
    $.get('/books', {'query': query, 'field': field}, function(data) {
        var table = $('#books tbody');
        table.empty();
        if (query === '') {  // if query empty
            window.location.reload();  // reload template
        } else {
            data.forEach(function(book) {
                var row = $('<tr></tr>');
                row.append($('<td></td>').text(book.id));
                row.append($('<td></td>').text(book.title));
                row.append($('<td></td>').text(book.author));
                row.append($('<td></td>').text(book.genre));
                row.append($('<td></td>').text(book.year));
                row.append($('<td></td>').text(book.stock));
                row.append($('<td></td>').text(book.availability));
                table.append(row);
            });
        }
    });
}


// Populate popup form fields with corresponding values of a selected member (members.html)
function editMember(member_id, name, email, address, phone){
    document.getElementById("form_id").value = member_id;
    document.getElementById("form_name").value = name;
    document.getElementById("form_email").value = email;
    document.getElementById("form_address").value = address;
    document.getElementById("form_phone").value = phone;
}


// Dynamic search with AJAX and jQuery (members.html)
function searchMember() {
    var query = $('#search').val(); 
    var field = $('#field').val();
    $.get('/members', {'query': query, 'field': field}, function(data) {
        var table = $('#members tbody');
        table.empty();
        if (query === '') {  // If query empty
            window.location.reload();  // Reload template
        } else {
            data.forEach(function(member) {
                var row = $('<tr></tr>');
                row.append($('<td></td>').text(member.member_id));
                row.append($('<td></td>').text(member.name));
                row.append($('<td></td>').text(member.email));
                row.append($('<td></td>').text(member.address));
                row.append($('<td></td>').text(member.phone));
                
                form = $('<form></form>').attr('action', '/members').attr('method', 'POST').on('click', function(e) {
                    if (!confirm("Completely remove member " + member.name + " (member ID: " + member.member_id + ") and all their details from library database?")) {
                        e.preventDefault();  // Prevent form submission if user cancels
                    }
                });
                input = $('<input>').attr("name", 'id').attr('value', member.member_id).hide()
                button = $('<button></button>').text('Remove').addClass('button').attr('name', 'button').attr('value','remove');

                form.append(input).append(button);  // Input & button inside form element
                
                row.append($('<td></td>').append(form));
                row.append($('<td></td>').append($('<button></button>').text('Edit').addClass('button btn-edit').click(function() {
                    toggle();
                    editMember(member.member_id, member.name, member.email, member.address, member.phone);
                })));   // Toggle and editForm functions appended along with Edit button class
                table.append(row);
            });
        }
    });
}