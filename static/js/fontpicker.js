var fonts = [['Sonsie One', 54],
             ['Poiret One', 80],
             ['Freckle Face', 80],
             ['Keania One', 80],
             ['Rye', 68],
             ['Play', 80],
             ['Miss Fajardose', 90],
             ['Yanone Kaffeesatz', 72]
            ];

var index = Math.floor(Math.random() * fonts.length);
var font_name = fonts[index][0];
var font_size = fonts[index][1];

$('#brand').css('font-family', font_name).css('font-size', font_size);

$(function() {
  $('#brand').show();
});

