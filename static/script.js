 // BOOKS, MEMBERS, CATALOGUE
 
 // Toggle blur & popup function (books.html/members.html)
 function toggle() {
    let blur = $('#blur');
    blur.toggleClass('active');
    let popup = $('#popup');
    popup.toggleClass('active');
}


// Populate popup form fields with corresponding values of a selected book (books.html)
function editBook(id, title, author, genre, year, stock) {
    $("#form_id").val(id);
    $("#form_title").val(title);
    $("#form_author").val(author);
    $("#form_genre").val(genre);
    $("#form_year").val(year);
    $("#form_stock").val(stock);
}


// Populate popup form fields with corresponding values of a selected member (members.html)
function editMember(member_id, name, email, address, phone) {
    $("#form_id").val(member_id);
    $("#form_name").val(name);
    $("#form_email").val(email);
    $("#form_address").val(address);
    $("#form_phone").val(phone);
}


// Show a warning if field in any popup form left empty (books and members)
$(document).ready(function() {
    $('#form_title, #form_author, #form_year, #form_stock, #form_name, #form_email, #form_address, #form_phone').blur(function() {
        if(!$(this).val()) {
            alert('All fields are required')
            return false
        }
    });
});

// Assign members and books table tbody elements to global variables for repopulating tables in searchBook() and searchMember() if query is empty
let tableBooks = {};
let tableMembers = {};
$(document).ready(function() {
    tableBooks = $('#books tbody').html();
    tableMembers = $('#members tbody').html();
});

// Dynamic search with AJAX (books.html)
function searchBook() {
    
    let query = $('#search').val();
    let field = $('#field').val();

    $.get('/books', {'query': query, 'field': field}, function(data) {
        let table = $('#books tbody');
        table.empty();

        // Repopulate table with original values if query is empty
        if (!query) {
            table.append(tableBooks);
        } else {
            // Iterate over data and populate rows
            data.forEach(function(book) {
                let row = $('<tr></tr>');
                row.append($('<td></td>').text(book.id));
                row.append($('<td></td>').text(book.title));
                row.append($('<td></td>').text(book.author));
                row.append($('<td></td>').text(book.genre));
                row.append($('<td></td>').text(book.year));
                row.append($('<td></td>').text(book.stock));
                
                // Form, input and button elements
                let form = $('<form></form>').attr('action', '/books').attr('method', 'POST').submit(function(e) {
                    if (!confirm('Completely remove \'' + book.title + '\' by ' + book.author + ' (book ID: ' + book.id + ') and all of its stock from library database?')) {
                        // Prevent form submission if user cancels
                        e.preventDefault();
                    }
                });
                let input = $('<input>').attr("name", 'id').attr('value', book.id).hide();
                let button = $('<button></button>').text('Remove').addClass('button').attr('name', 'button').attr('value','remove');
                
                // Append form along with input and button elements to a row
                row.append($('<td></td>').append(form.append(input).append(button)));

                // Toggle and editBook functions appended to a table row along with Edit button and its class
                row.append($('<td></td>').append($('<button></button>').text('Edit').addClass('button btn-edit').click(function() {
                    toggle();
                    editBook(book.id, book.title, book.author, book.genre, book.year, book.stock);
                })));

                // Add row to a table
                table.append(row);
            });
        }
    });
}


// Dynamic search with AJAX using json response from books endpoint (catalogue.html)
function searchCatalogue() {
    let query = $('#search').val();
    let field = $('#field').val();
    $.get('/books', {'query': query, 'field': field}, function(data) {
        let table = $('#books tbody');
        table.empty();

        // Repopulate table with original values if query is empty
        if (query === '') {
            table.append(tableBooks);
        } else {
            // Iterate over data and populate rows
            data.forEach(function(book) {
                let row = $('<tr></tr>');
                row.append($('<td></td>').text(book.id));
                row.append($('<td></td>').text(book.title));
                row.append($('<td></td>').text(book.author));
                row.append($('<td></td>').text(book.genre));
                row.append($('<td></td>').text(book.year));
                row.append($('<td></td>').text(book.stock));
                row.append($('<td></td>').text(book.available));
                table.append(row);
            });
        }
    });
}


// Dynamic search with AJAX (members.html)
function searchMember() {
    let query = $('#search').val(); 
    let field = $('#field').val();
    $.get('/members', {'query': query, 'field': field}, function(data) {
        let table = $('#members tbody');
        table.empty();

        // Repopulate table with original values if query is empty
        if (!query) {
            table.append(tableMembers);
        } else {
            // Iterate over data and populate rows
            data.forEach(function(member) {
                let row = $('<tr></tr>');
                row.append($('<td></td>').text(member.member_id));
                row.append($('<td></td>').text(member.name));
                row.append($('<td></td>').text(member.email));
                row.append($('<td></td>').text(member.address));
                row.append($('<td></td>').text(member.phone));
                
                // Form, input and button elements
                let form = $('<form></form>').attr('action', '/members').attr('method', 'POST').submit(function(e) {
                    if (!confirm("Completely remove member " + member.name + " (member ID: " + member.member_id + ") and all their details from library database?")) {
                        // Prevent form submission if user cancels
                        e.preventDefault();
                    }
                });
                let input = $('<input>').attr("name", 'id').attr('value', member.member_id).hide();                
                let button = $('<button></button>').text('Remove').addClass('button').attr('name', 'button').attr('value','remove');
                
                // Append form along with input and button elements to a row
                row.append($('<td></td>').append(form.append(input).append(button)));

                // Toggle and editMember functions appended along with Edit button and its class
                row.append($('<td></td>').append($('<button></button>').text('Edit').addClass('button btn-edit').click(function() {
                    toggle();
                    editMember(member.member_id, member.name, member.email, member.address, member.phone);
                })));

                // Add row to a table
                table.append(row);
            });
        }
    });
}


// CHECKOUT

function checkoutMemberSearch() {

    let query = $('#searchMember').val();

    // Query empty
    if (!query) {                         
        $('.collapseCh').hide();         // Hide collapsable element
        $('#member tbody').empty();    // Clear table's body element
        $('#searchMember').focus();    // Focus back (caret) on input element
        return                            
    }
    $.get('/checkout', {'queryMember': query}, function(data) {
        let found = false;
        // Assign a row element and its class to a row variable
        let row = $('<tr></tr>').addClass('row-member-ch');
        // Show collapsable element
        $('.collapseCh').show();
        // Iterate over data response (array of objects)
        data.forEach(function(element) {
            // Query exists in data
            if(query == element.member_id) {
                       
                // Populate rows with members details and add cancel button
                row.append($('<td id="memberId"></td>').text(element.member_id));
                row.append($('<td></td>').text(element.name));
                row.append($('<td></td>').text(element.email));
                row.append($('<td></td>').text(element.address));
                row.append($('<td></td>').text(element.phone));
                // Also used in script below to check max amount of books that can be issued to a member (6):
                row.append($('<td id="borrowed"></td>').text(element.borrowed));
                // Cancel button
                row.append($('<td></td>').html('<button class="btn-cancel-member" id="cancelMember">Cancel</button>'));
                // Add hidden input element with member id value to the form element at the bottom of the template
                $('#checkout').append($('<input name="memberId" hidden>').attr('value', element.member_id));

                // Add to/replace existing content of tbody element (so only one member will show at time) 
                $('#member tbody').html(row);
                // Set found variable to true
                found = true; 
                // Move focus (caret) to searchBook input element
                $('#searchBook').focus();
            }
        }); 
        // Query doesn't exists in data
        if (!found) {
            $('.collapseCh').hide();
            $('#member tbody').empty();
            $('#searchMember').val('');
            alert('Member ID does not exist in library database');
            $('#searchMember').focus();
            // If book in collapseable element already searched for, clear that element and search value
            $('#book tbody').empty();
            $('#searchBook').val('');
        }
        // Remove member (clear table's body element) if cancel selected
        $('#cancelMember').click(function() {
            $('.collapseCh').hide();
            $('#member tbody').empty();
            $('#searchMember').val('');
            $('#searchMember').focus();
            // If book in collapseable element already searched for, clear that element and search value
            $('#book tbody').empty();
            $('#searchBook').val('');
            // Clear any added books in collapseable element
            $('#addedBooks tbody').empty();
        });
    });
}


function checkoutBookSearch() {

    let query = $('#searchBook').val();

    // Query empty
    if (!query) {
        $('#book tbody').empty();    // Clear table's body element
        $('#searchBook').focus();    // Focus back (caret) on input element
        return                            
    }
    $.get('/checkout', {'queryBook': query}, function(data) {
        let found = false;
        // Assign a row element and its class to a row variable
        let row = $('<tr></tr>');
        
        // Iterate over data response (books)
        data[0].forEach(function(element) {
            // Query exists in data
            if(query == element.id) {
                       
                // Populate rows with book details and add cancel and add book buttons
                row.append($('<td></td>').text(element.id));
                row.append($('<td></td>').text(element.title));
                row.append($('<td></td>').text(element.author));
                row.append($('<td></td>').text(element.genre));
                row.append($('<td></td>').text(element.year));
                row.append($('<td class="available"></td>').text(element.available));
                row.append($('<td></td>').html('<button class="btn-book" id="addBook">Add Book</button>'));
                row.append($('<td></td>').html('<button class="btn-book" id="cancelBook">Cancel</button>'));
                // Add to/replace existing content of tbody element (so only one book will show at time)
                $('#book tbody').html(row);
                // Set found variable to true
                found = true;
                

                // Add books block
                $('#addBook').click(function() {

                    let alreadyAdded = false;
                    let alreadyBorrowed = false;

                    // Loop through each row of added books and check if book already added
                    $('#addedBooks tbody tr').each(function() {
                        if ($(this).find('.check-Id').text() == element.id) {
                            alreadyAdded = true;
                            // As soon as book match found break out of the loop
                            return false;
                        }
                    });
                    // Iterate over transactions list and check if book with the same id has already being borrowed but not returned
                    data[1].forEach(function(t) {
                        if(t.borrower_id == $('#memberId').text() && t.book_id == element.id && t.type == 'borrow') {
                           alreadyBorrowed = true;
                           return false;
                        }
                    });
                    // Book already borrowed
                    if (alreadyBorrowed) {
                        alert('Book has already been checked out to this member')
                    }
                    // Book already added
                    else if (alreadyAdded) {
                        alert('Book already added');
                    }
                    // Book current stock == 0
                    else if($('.available').text() <= 0) {
                        alert('Book currently unavailable')
                    } else {
                        // Add book to table
                        let rowAdded = $('<tr></tr>').addClass('row-data');
                        rowAdded.append($('<td class="check-Id"></td>').text(element.id));
                        rowAdded.append($('<td></td>').text(element.title));
                        rowAdded.append($('<td></td>').text(element.author));
                        rowAdded.append($('<td></td>').text(element.genre));
                        rowAdded.append($('<td></td>').text(element.year));
                        rowAdded.append($('<td></td>').html('<button class="btn-remove-book">Remove</button>'));
                        $('#addedBooks tbody').append(rowAdded);
                        // Add hidden input elements with book id values to the form element
                        $('#checkout').append($('<input name="bookId" hidden>').attr('value', element.id));
                        // Clear search result and move focus back to search 
                        $('#book tbody').empty();
                        $('#searchBook').val('');
                        $('#searchBook').focus();
                    }
                });
            }
        });
        // Remove added book by deleting the closest row to remove button, and remove corresponding input element from form element
        $('#addedBooks tbody').on('click', '.btn-remove-book', function() {
            $(this).closest('tr').remove();

            let formInputId = $(this).closest('tr').children('td').eq(0).text();
            $('#checkout input').each(function() {
                if($(this).val() == formInputId) {
                    $(this).remove();
                }
            })
            
           
        });

        // Query doesn't exists in data
        if (!found) {
            $('#book tbody').empty();
            $('#searchBook').val('');
            alert('Book ID does not exist in library database');
        }
        // Cancel book search (clear table's body element) if cancel selected
        $('#cancelBook').click(function() {
            $('#book tbody').empty();
            $('#searchBook').val('');
            $('#searchBook').focus();
        }); 
    });
}

// Trigger a click event on a search buttons when Enter is pressed
$(document).ready(function() {
    $('#searchMember').keypress(function(e) {
        if(e.which == 13) {
        $('#memberSearch').click();
        }
    });
    $('#searchBook').keypress(function(e) {
        if(e.which == 13) {
        $('#bookSearch').click();
        }
    });
});

// Check different parameters before submiting
$(document).ready(function() { 
    $('#checkout').submit(function(event) {
        
        // Number of rows (added books)
        let counter = $('.check-Id').length;

        // No books added
        if(counter == 0) {
            // Show alert and prevent submission
            alert('No books added yet');
            event.preventDefault();

        // Member can not have more than 6 books at a time. Books that are previously borrowed but not returned yet are taken into account
        } else if((parseInt($('#borrowed').text()) + counter) > 6) {
            alert('Maximum number of books a member can hold at a time is 6');
            event.preventDefault();
        }
        // Else prompt for confirmation
        else {
            // If ok selected -> submit and let backend do the rest
            if(confirm('Confirm checkout')) {
            
            }
            // If cancel selected prevent submission
            else {
                event.preventDefault();
            }
        }
    });
});


// INDEX (BOOK RETURNS)

$(document).ready(function() {

    // Dynamic search on index template (member id)

    let tableReturns = $('#returns tbody').html();

    $('#searchReturns').keyup(function() {

        let query = $('#searchReturns').val();

        // In case of multiple keystokes populate table with original values (show all) so query can continue (multiple digits query)
        $('#returns tbody').html(tableReturns);
        // Hide all rows that don't match the query
        $('.row-data-index').each(function() {
            if (query != $(this).find('.memId').text()) {
                $(this).hide();
            }
        });
        // If query deleted repopulate table (show all again)
        if (!query) {
            $('#returns tbody').html(tableReturns);
        }
    });


    // Book returns

    $('.row-data-index').click(function () {

        // Clear table body element and remove all hidden input elements (in case they were already populated from previous click)
        $('#borrowed tbody').empty();
        $('#inputMemId').remove();
        $('.inputAll').remove();
        
        // Get child's value (member id and name) of a row clicked on
        let memId = $(this).find('.memId').text();
        let memName = $(this).find('.memName').text();

        // Add member's name to the offcanvas element where borrowed books will be listed
        $('#offcanvasBottomLabel').text(memName);

        // Ajax post request (json response: books and transactions lists)
        $.post('/', dataType="json", function(data) {
            
            // Iterate over transactions list and compare its borrowed books ids with list of books ids for a selected member
            data[1].forEach(function(transaction) {
                data[0].forEach(function(books) {
                    if(memId == transaction.borrower_id && transaction.type == 'borrow' && books.id == transaction.book_id) {
                        // Assaign date object to a date variable
                        let date = new Date(transaction.time);
                        // Set due date (3 weeks after book is borrowed)
                        date.setDate(date.getDate() + 21);
                        // Get date portion of a date object
                        let dueDate = date.toDateString()
                        // Current time
                        let currentDate = new Date($.now());
                        
                        let row = $('<tr></tr>').addClass('row-return');
                        row.append($('<td></td>').text(books.id));
                        row.append($('<td></td>').text(books.title));
                        row.append($('<td></td>').text(books.author));
                        row.append($('<td></td>').text(books.genre));
                        row.append($('<td></td>').text(books.year));
                        // If due date or past due date show date in red color
                        if(date <= currentDate){
                            row.append($('<td class="red"></td>').text(dueDate));
                        }
                        else {
                            row.append($('<td></td>').text(dueDate));
                        }

                        // Initialize form, input and button variables
                        let form = $('<form></form>').attr('action', '/').attr('method', 'POST').submit(function(e) {
                            if (!confirm("Return book " + books.title + "?")) {
                                // Prevent form submission if user cancels
                                e.preventDefault();
                            }
                        });
                        let inputBook = $('<input>').attr("name", 'id').attr('value', books.id).hide(); 
                        let inputMember = $('<input>').attr("name", 'memberId').attr('value', memId).hide();
                        let button = $('<button></button>').text('Return').addClass('btn-return-book');
                        
                        // Append form along with inputs and button elements to a row
                        row.append($('<td></td>').append(form.append(inputBook).append(inputMember).append(button)));

                        // Add row to a tbody element
                        $('#borrowed tbody').append(row);

                        // Add input element(s) to a form (id="returnAll") with borrowed book(s) id(s)
                        $('#returnAll').append(($('<input>')).attr('class','inputAll').attr('name', 'all_ids').attr('value', books.id).hide());  
                    }
                });
            }); 
            // Add input element to a form (id="returnAll") with member id
            $('#returnAll').append(($('<input>')).attr('id','inputMemId').attr('name', 'memberId').attr('value', memId).hide());

        });
    });
});


// LMS MANAGEMENT - TRANSACTIONS HISTORY (FILTERS)

$(document).ready(function () {
    
    // Remember whole table content on page load
    let table = $('#historyTable tbody').html();
    // Add 'Libraran' as a disabled and selected option to the select element 
    $('.librarian-filter #disabled').text('Librarian').prop('selected', true);


    // Filter out by transaction type

    $('#borrowed').click(function() {

        // Show rows with borrowed class and hide rows with returned class (remove and add .hiddenTxn classes as well - to be used in other filters)
        $('#historyTbody').find('.borrowed').removeClass('hiddenTxn').css('display', '');
        $('#historyTbody').find('.returned').addClass('hiddenTxn').css('display', 'none');

        // If other filter(s) already applied and click event unhides some of those rows in a step above, hide those rows again
        $('#historyTbody').find('.hiddenLibrarian').css('display', 'none');
        $('#historyTbody').find('.hiddenBook').css('display', 'none');
        $('#historyTbody').find('.hiddenMember').css('display', 'none');

    });

    $('#returned').click(function() {
        // Hide rows with borrowed class and show rows with returned class (add and remove .hiddenTxn classes as well)
        $('#historyTbody').find('.borrowed').addClass('hiddenTxn').css('display', 'none');
        $('#historyTbody').find('.returned').removeClass('hiddenTxn').css('display', '');

        // If other filter(s) already applied and click event unhides some of those rows in a step above, hide those rows again
        $('#historyTbody').find('.hiddenLibrarian').css('display', 'none');
        $('#historyTbody').find('.hiddenBook').css('display', 'none');
        $('#historyTbody').find('.hiddenMember').css('display', 'none');
    });


    // Filter out by book ID
    $('#queryBookId').keyup(function() {

        // If more then one keyup (if query has multiple digits), unhide those rows that were hidden before so new comparison can be made in the script below
        $('#historyTable tbody').find($('.hiddenBook')).css('display', '').removeClass('hiddenBook');

        // If query unhides rows that should stay hidden via other filters, hide them again 
        $('#historyTable tbody').find($('.hiddenMember')).css('display', 'none');
        $('#historyTable tbody').find($('.hiddenTxn')).css('display', 'none');
        $('#historyTable tbody').find($('.hiddenLibrarian')).css('display', 'none');

        // Iterate over rows, find all bookId values and compare to query
        $('#historyTbody tr').each(function() {
            if($(this).find('.bookId').text() != $('#queryBookId').val()) {

                // Hide all that don't match the query and add class hiddenBook
                $(this).addClass('hiddenBook').css('display', 'none');
            }
        });
        // If query deleted, show all hidden books and remove hiddenBook class
        if ($('#queryBookId').val().length === 0) {
            $('#historyTable tbody').find($('.hiddenBook')).css('display', '').removeClass('hiddenBook');

            // If deleted query unhides rows that should stay hidden via other filters, hide them again
            $('#historyTable tbody').find($('.hiddenMember')).css('display', 'none');
            $('#historyTable tbody').find($('.hiddenTxn')).css('display', 'none');
            $('#historyTable tbody').find($('.hiddenLibrarian')).css('display', 'none');
        }
    });


    // Filter out by member ID (check comments above in the book ID filter)
    $('#queryMemberId').keyup(function() {
        $('#historyTable tbody').find($('.hiddenMember')).css('display', '').removeClass('hiddenMember');

        $('#historyTable tbody').find($('.hiddenBook')).css('display', 'none');
        $('#historyTable tbody').find($('.hiddenTxn')).css('display', 'none');
        $('#historyTable tbody').find($('.hiddenLibrarian')).css('display', 'none');

        $('#historyTbody tr').each(function() {
            if($(this).find('.memberId').text() != $('#queryMemberId').val()) {
                $(this).addClass('hiddenMember').css('display', 'none');
            }
        });
        if ($('#queryMemberId').val().length === 0) {            
            $('#historyTable tbody').find($('.hiddenMember')).css('display', '').removeClass('hiddenMember');

            $('#historyTable tbody').find($('.hiddenBook')).css('display', 'none');
            $('#historyTable tbody').find($('.hiddenTxn')).css('display', 'none');
            $('#historyTable tbody').find($('.hiddenLibrarian')).css('display', 'none');
        }
    });


    // Filter out by librarian name

    // Extract distinct librarian names and add them to the select element
    // Initialize allNames object
    let allNames = {}
    // Iterate over rows
    $('#historyTbody tr').each(function() {

        // Assign librarian name from current row to the name variable
        let name = $(this).find('.staff-name').text();

        // If name not true
        if (!allNames[name]) {

            // Add it as an option to the select element
            $('.librarian-filter').append($('<option>'+name+'</option>)').addClass('lib_name'))

            // Set added name to true
            allNames[name] = true;
        }
    });

    // Filter (trigger event on option change)
    $('.librarian-filter').change(function() {    

        // Value of selected option (librarian name)
        let option = ($(this).val())

        $('#historyTbody tr').each(function() {            
            
            // If librarian names in the rows do not match selected one
             if($(this).find('.staff-name').text() != option) {
                // Hide those rows and add classes .hiddenLibrarian (also used in transaction type filter above)
                $(this).addClass('hiddenLibrarian').css('display', 'none');
            }
            // Else if they match
            else {
                // Show those rows and remove class .hiddenLibrarian (if exists)
                $(this).removeClass('hiddenLibrarian').css('display', '');                
            }
        });
        // If any rows that were hidden via other filters are being revealed in the loop above, hide them again
        $('#historyTbody').find('.hiddenTxn').css('display', 'none');
        $('#historyTbody').find('.hiddenBook').css('display', 'none');
        $('#historyTbody').find('.hiddenMember').css('display', 'none');
    });


    // Sort rows by time DESC or ASC (by default, table is sorted DESC on page load, so I'm only switching the rows)

    // Arrow pointing down for DESC order on page load
    $('#arrowUp').hide();
    $('#arrowDown').show();

    $('#sortDate').click(function() {

        // Toggle arrows on click
        $('#arrowUp').toggle();
        $('#arrowDown').toggle();
        
        let rows = $('#historyTbody').find('tr');

        // Make half times less iterations than there are number of rows (rounded to the nearest integer)
        for (let i = 0; i < Math.floor(rows.length / 2); i++) {
            
            // Initialize temporary variables, value is always first row that has not been switched yet 
            // Class and attribute are assigned as well to preserve style of the rows and potentially applied filters
            let temp = $(rows[i]).html();
            let tempClass = $(rows[i]).attr('class');
            let tempCss = $(rows[i]).css('display');

            // Add last row that hasn't switched yet to the first row that hasn't switched yet (along with class and attribute)
            $(rows[i]).html($(rows[rows.length - 1 - i]).html());
            $(rows[i]).attr('class', $(rows[rows.length - 1 - i]).attr('class'));
            $(rows[i]).css('display', $(rows[rows.length - 1 - i]).css('display'));
            
            // Add first (temporary variable) to last
            $(rows[rows.length - 1 - i]).html(temp);
            $(rows[rows.length - 1 - i]).attr('class', tempClass);
            $(rows[rows.length - 1 - i]).css('display', tempCss);
        }        
    });


    // Reset all filters
    $('.clear-filters').click(function() {
        $('#historyTable tbody').html(table);
        $('#borrowed').prop('checked', false);
        $('#returned').prop('checked', false);
        $('#queryBookId').val('');
        $('#queryMemberId').val('');
        $('.librarian-filter #disabled').text('Librarian').prop('selected', true);
        $('#arrowUp').hide();
        $('#arrowDown').show();
    })
});