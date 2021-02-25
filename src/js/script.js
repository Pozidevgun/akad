$(document).ready(function(){
  const nav = $(".header");
  let introH = 920 ; // из-за слика так бы написал  $(".container--header").innerHeight()
  let scrollOffset = $(window).scrollTop();
  
/*fixed header*/
	checkScroll(scrollOffset);
	$(window).on("scroll", function(){
			scrollOffset = $(this).scrollTop();
			checkScroll(scrollOffset);
	});
	function checkScroll(scrollOffset) {
		scrollOffset = $(this).scrollTop();
			if(scrollOffset >= introH){
        nav.addClass("header--fixed");
			}else{
				nav.removeClass("header--fixed");
			}
  }
  //slider
  $('.slider--header').slick({
    dots: true,
  	slidesToShow: 1,
  	slidesToScroll: 1,
  	responsive: [
    {
      breakpoint: 1024,
      settings: {
        infinite: true,
        arrows:  false  
      }
    }
  ]
  });
  //slider
  $('.slider--partners').slick({
    dots: true,
  	slidesToShow: 1,
    slidesToScroll: 1,
    infinite: true,
    arrows: false	
  });

  
  $('.nav-burger').on('click',function(){
    $('.nav').toggleClass('nav--close').toggleClass('nav--open');
  });
  $('.button-choose--toggle').on('click',function(){ //portfolio
    $('.button-choose--toggle').not(this).removeClass('button-choose--active');
    $(this).toggleClass('button-choose--active');
  });
  $('.post__link').on('click',function(){ //post
    $('.post__link').not(this).removeClass('post__link--active');
    $(this).toggleClass('post__link--active');
  });
  $('.button-choose--grey').on('click',function(){ //tags
    $(this).toggleClass('button-choose--active');
  });

  $('.post').each(function() {
        let ths = $(this);
        ths.find('.post__article').not(':first').hide();
        ths.find('.post__link').click(function() {
          ths.find('.post__link').removeClass('.post__link--active').eq($(this).index()).addClass('.post__link--active');
          ths.find('.post__article').hide().eq($(this).index()).fadeIn()
        }).eq(0).addClass('post__article--show');
      });
  
 
});