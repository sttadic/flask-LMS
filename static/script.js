 // Javascript toggle blur & popup function (books.html/members.html)
 function toggle() {
    let blur = document.querySelector('#blur');
    blur.classList.toggle('active');
    let popup = document.querySelector('#popup');
    popup.classList.toggle('active');
};


// Populate popup form fields with corresponding values of a selected book (books.html)
function editBook(id, title, author, genre, year, stock) {
    document.querySelector("#form_id").value = id;
    document.querySelector("#form_title").value = title;
    document.querySelector("#form_author").value = author;
    document.querySelector("#form_genre").value = genre;
    document.querySelector("#form_year").value = year;
    document.querySelector("#form_stock").value = stock;
};


// Dynamic search with AJAX and jQuery (books.html)
function searchBook() {
    let query = $('#search').val();
    let field = $('#field').val();
    $.get('/books', {'query': query, 'field': field}, function(data) {
        let table = $('#books tbody');
        table.empty();
        if (!query) {                       // If query empty
            window.location.reload();       // Reload template
        } else {
            data.forEach(function(book) {
                let row = $('<tr></tr>');
                row.append($('<td></td>').text(book.id));
                row.append($('<td></td>').text(book.title));
                row.append($('<td></td>').text(book.author));
                row.append($('<td></td>').text(book.genre));
                row.append($('<td></td>').text(book.year));
                row.append($('<td></td>').text(book.stock));
                
                form = $('<form></form>').attr('action', '/books').attr('method', 'POST').on('click', function(e) {
                    if (!confirm('Completely remove \'' + book.title + '\' by ' + book.author + ' (book ID: ' + book.id + ') and all of its stock from library database?')) {
                        // Prevent form submission (default behavior) if user cancels
                        e.preventDefault();
                    };
                });
                input = $('<input>').attr("name", 'id').attr('value', book.id).hide();
                button = $('<button></button>').text('Remove').addClass('button').attr('name', 'button').attr('value','remove');
                // Input & button inside form element
                form.append(input).append(button);
                
                row.append($('<td></td>').append(form));
                // Toggle and editBook functions appended to a table row along with Edit button and its class
                row.append($('<td></td>').append($('<button></button>').text('Edit').addClass('button btn-edit').click(function() {
                    toggle();
                    editBook(book.id, book.title, book.author, book.genre, book.year, book.stock);
                })));
                table.append(row);
            });
        };
    });
};


// Dynamic search with AJAX and jQuery (catalogue.html)
function searchCatalogue() {
    let query = $('#search').val();
    let field = $('#field').val();
    $.get('/books', {'query': query, 'field': field}, function(data) {
        let table = $('#books tbody');
        table.empty();
        if (query === '') {                 // if query empty
            window.location.reload();       // reload template
        } else {
            data.forEach(function(book) {
                let row = $('<tr></tr>');
                row.append($('<td></td>').text(book.id));
                row.append($('<td></td>').text(book.title));
                row.append($('<td></td>').text(book.author));
                row.append($('<td></td>').text(book.genre));
                row.append($('<td></td>').text(book.year));
                row.append($('<td></td>').text(book.stock));
                row.append($('<td></td>').text(book.availability));
                table.append(row);
            });
        };
    });
};


// Populate popup form fields with corresponding values of a selected member (members.html)
function editMember(member_id, name, email, address, phone) {
    document.querySelector("#form_id").value = member_id;
    document.querySelector("#form_name").value = name;
    document.querySelector("#form_email").value = email;
    document.querySelector("#form_address").value = address;
    document.querySelector("#form_phone").value = phone;
};


// Dynamic search with AJAX and jQuery (members.html)
function searchMember() {
    let query = $('#search').val(); 
    let field = $('#field').val();
    $.get('/members', {'query': query, 'field': field}, function(data) {
        let table = $('#members tbody');
        table.empty();
        if (!query) {                       // If query empty
            window.location.reload();       // Reload template
        } else {
            data.forEach(function(member) {
                let row = $('<tr></tr>');
                row.append($('<td></td>').text(member.member_id));
                row.append($('<td></td>').text(member.name));
                row.append($('<td></td>').text(member.email));
                row.append($('<td></td>').text(member.address));
                row.append($('<td></td>').text(member.phone));
                
                form = $('<form></form>').attr('action', '/members').attr('method', 'POST').on('click', function(e) {
                    if (!confirm("Completely remove member " + member.name + " (member ID: " + member.member_id + ") and all their details from library database?")) {
                        // Prevent form submission if user cancels
                        e.preventDefault();
                    };
                });
                input = $('<input>').attr("name", 'id').attr('value', member.member_id).hide();
                button = $('<button></button>').text('Remove').addClass('button').attr('name', 'button').attr('value','remove');
                // Input & button inside form element
                form.append(input).append(button);
                
                row.append($('<td></td>').append(form));
                // Toggle and editMember functions appended along with Edit button and its class
                row.append($('<td></td>').append($('<button></button>').text('Edit').addClass('button btn-edit').click(function() {
                    toggle();
                    editMember(member.member_id, member.name, member.email, member.address, member.phone);
                })));
                table.append(row);
            });
        };
    });
};