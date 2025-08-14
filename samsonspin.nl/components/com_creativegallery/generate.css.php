

.creative-gallery-container .creative-gallery-seperator {
	width: 100%;
	height: 0px;
	border-width: 0;
	border-top-width: 1px;
	border-style : dotted;
	border-color: rgba(158,158,158,1);
	margin: 20px 0px;
}

.creative-gallery-container .creative-gallery-seperator-vertical {
	width: 0px;
    border-width: 0;
	border-left-width: 1px;
	border-style : dotted;
	border-color: rgba(158,158,158,1);
	margin: 0px 20px;
    float: left;
}

.creative-gallery-container.creative-gallery-container {
    display: block;
    height: auto;
    background-color: rgba(36,36,36,1);
    padding: 20px ;
    border:  1px solid rgba(0,0,0,1);
    border-radius: 0px;
    -webkit-box-shadow: 0px 0px 0px 0px rgba(255,255,255,0.5);
    -moz-box-shadow: 0px 0px 0px 0px rgba(255,255,255,0.5);
    -ms-box-shadow: 0px 0px 0px 0px rgba(255,255,255,0.5);
    -o-box-shadow: 0px 0px 0px 0px rgba(255,255,255,0.5);
    box-shadow: 0px 0px 0px 0px rgba(255,255,255,0.5);
}

.creative-gallery-container .creative-gallery-image-wrapper {
    overflow: hidden;
    position: relative;
    width: 100%;
    height: 100%;
    /*border: 1px solid rgba(255,255,255,0.6);*/
    border-radius: 0% ;
    -webkit-transition: all 0.5s;
    -moz-transition: all 0.5s;
    -ms-transition: all 0.5s;
    -o-transition: all 0.5s;
    transition: all 0.5s;
    -webkit-mask: URL("/components/com_creativegallery/assets/images/dummy.png") ;
}

.creative-gallery-container .creative-gallery-image-wrapper img {
    border-radius: 0% ;
    -webkit-transition: all 0.5s;
    -moz-transition: all 0.5s;
    -ms-transition: all 0.5s;
    -o-transition: all 0.5s;
    transition: all 0.5s;
}

.creative-gallery-container ul.gallery {
    -webkit-transition: all 0.5s;
    -moz-transition: all 0.5s;
    -ms-transition: all 0.5s;
    -o-transition: all 0.5s;
    transition: all 0.5s;
}

.creative-gallery-container li.visible {
    -webkit-box-shadow: 0px 0px 5px 1px rgba(0,0,0,1);
    -moz-box-shadow: 0px 0px 5px 1px rgba(0,0,0,1);
    -ms-box-shadow: 0px 0px 5px 1px rgba(0,0,0,1);
    -o-box-shadow: 0px 0px 5px 1px rgba(0,0,0,1);
    box-shadow: 0px 0px 5px 1px rgba(0,0,0,1);
	border: 1px solid rgba(255,255,255,0.6);
	border-radius: 0% ;
	-webkit-transition: all 0.5s;
    -moz-transition: all 0.5s;
    -ms-transition: all 0.5s;
    -o-transition: all 0.5s;
    transition: all 0.5s;
}

.creative-gallery-container li.visible:hover {
    border-radius: 0% ;
    border: 1px solid rgba(255,255,255,1);
    -webkit-box-shadow: 0px 0px 7px 1px rgba(0,0,0,1);
    -moz-box-shadow: 0px 0px 7px 1px rgba(0,0,0,1);
    -ms-box-shadow: 0px 0px 7px 1px rgba(0,0,0,1);
    -o-box-shadow: 0px 0px 7px 1px rgba(0,0,0,1);
    box-shadow: 0px 0px 7px 1px rgba(0,0,0,1);
}

.creative-gallery-container li.visible.current {
	border-radius: 0% ;
	border-color: rgba(255,255,255,1);
}



.creative-gallery-container .creative-gallery-image-wrapper .overlay {
	position: absolute;
	top: 0;
	left: 0;
    width: 100%;
    height: 100%;
    display: none;
}

.creative-gallery-container li.visible:hover .creative-gallery-image-wrapper {
	border-radius: 0% ;
	border-color: rgba(255,255,255,1);
}


.creative-gallery-container li.visible:hover img {
    border-radius: 0% ;
}

.creative-gallery-container .creative-gallery-image-main-wrapper {
	border-radius: 0% ;
    overflow: hidden;
    -webkit-transition: all 0.5s;
    -moz-transition: all 0.5s;
    -ms-transition: all 0.5s;
    -o-transition: all 0.5s;
    transition: all 0.5s;
    height: 100%;
    width: 100%;
    position: absolute;
    top: 0px;
    left: 0px;
}

.creative-gallery-container li.visible:hover .creative-gallery-image-main-wrapper {
	border-radius: 0% ;

}

.creative-gallery-container .creative-gallery-text {
	display : none;
	-webkit-text-shadow:  1px 1px 0px rgba(0,0,0,0.5);
	-moz-text-shadow:  1px 1px 0px rgba(0,0,0,0.5);
	-ms-text-shadow:  1px 1px 0px rgba(0,0,0,0.5);
	-o-text-shadow:  1px 1px 0px rgba(0,0,0,0.5);
	text-shadow:  1px 1px 0px rgba(0,0,0,0.5);
    letter-spacing: 0px;
    word-spacing: 0px;
    line-height: 160%;
    color:  rgba(255,255,255,1);
    font-size: 12px;
    direction:  ltr;
    unicode-bidi: normal;
    text-decoration: none;
    text-transform: none;
}





/*Icon Styles*/

.creative-gallery-container .creative-gallery-icon {
    display: block;
    position: absolute;
	cursor: pointer;
	background-repeat: no-repeat;
    background-position: center center;
	width: 35px;
    height: 35px;
    -webkit-box-shadow: 0px 0px 3px 1px rgba(0,0,0,0.6) ;
    -moz-box-shadow: 0px 0px 3px 1px rgba(0,0,0,0.6) ;
    -ms-box-shadow: 0px 0px 3px 1px rgba(0,0,0,0.6) ;
    -o-box-shadow: 0px 0px 3px 1px rgba(0,0,0,0.6) ;
    box-shadow: 0px 0px 3px 1px rgba(0,0,0,0.6) ;
    border: 1px solid rgba(255,255,255,0.45);
    border-radius: 50%;
    background-color: rgba(0,0,0,0.45);
    background-size: 50%;
    -webkit-transition: all 0.5s;
    -moz-transition: all 0.5s;
    -ms-transition: all 0.5s;
    -o-transition: all 0.5s;
    transition: all 0.5s;
}

.creative-gallery-container .creative-gallery-image-wrapper .creative-gallery-icon:hover {
    -webkit-transform: rotate(20deg) scale(1.2)!important;
    -ms-transform: rotate(20deg) scale(1.2)!important;;
    -o-transform: rotate(20deg) scale(1.2)!important;;
    transform: rotate(20deg) scale(1.2)!important;;
}

.creative-gallery-container .creative-gallery-icon-zoom {
	display:none!important;	background-image: URL("/components/com_creativegallery/assets/images/image_icons/zoom1.png");
    top: -17.5px;
    left: -42.5px;
    -webkit-transform: rotateY(90deg); -ms-transform: rotateY(90deg); -o-transform: rotateY(90deg); transform: rotateY(90deg);;

}

.creative-gallery-container .creative-gallery-icon-link {
	display:none!important;	background-image: URL("/components/com_creativegallery/assets/images/image_icons/link1.png");
    top: -17.5px;
    left: 7.5px;
    -webkit-transform: rotateY(90deg); -ms-transform: rotateY(90deg); -o-transform: rotateY(90deg); transform: rotateY(90deg);;



}

.creative-gallery-container .creative-gallery-image-wrapper:hover .creative-gallery-icon-zoom {
    top:  -17.5px;
    left: -42.5px;
    -webkit-transform: rotateY(0deg); -ms-transform: rotateY(0deg); -o-transform: rotateY(0deg); transform: rotateY(0deg);;
}

.creative-gallery-container .creative-gallery-image-wrapper:hover .creative-gallery-icon-link {
    top:  -17.5px;
    left: 7.5px;
    -webkit-transform: rotateY(0deg); -ms-transform: rotateY(0deg); -o-transform: rotateY(0deg); transform: rotateY(0deg);;
}

/*Tags Styles*/

.creative-gallery-container .creative-gallery-tag {
	display : inline-block;
	cursor : pointer;
	margin: 0 10px 0;
	padding: 7px 15px ;
	background-color: rgba(71,71,71,1);
	border: 1px solid rgba(135,135,135,1);
	border-radius: 1px;
	-webkit-box-shadow: 0px 0px 3px 1px rgba(10,10,10,1) ;
	-moz-box-shadow: 0px 0px 3px 1px rgba(10,10,10,1) ;
	-ms-box-shadow: 0px 0px 3px 1px rgba(10,10,10,1) ;
	-o-box-shadow: 0px 0px 3px 1px rgba(10,10,10,1) ;
	box-shadow: 0px 0px 3px 1px rgba(10,10,10,1) ;
	-webkit-text-shadow:  1px 2px 1px rgba(0,0,0,0.7);
	-moz-text-shadow:  1px 2px 1px rgba(0,0,0,0.7);
	-ms-text-shadow:  1px 2px 1px rgba(0,0,0,0.7);
	-o-text-shadow:  1px 2px 1px rgba(0,0,0,0.7);
	text-shadow:  1px 2px 1px rgba(0,0,0,0.7);
	letter-spacing: 0px;
	word-spacing: 0px;
	color:  rgba(255,255,255,0.85);
	line-height: 100%;
	font-size: 12px;
	direction:  ltr;
	unicode-bidi: normal;
	text-decoration: none;
	text-transform: none;
	transition: all 0.4s;
	-webkit-transition: all 0.4s;
	-moz-transition: all 0.4s;
	-ms-transition: all 0.4s;
	-o-transition: all 0.4s;
}

/*Tags Styles Hover*/

.creative-gallery-container .creative-gallery-tag:hover {
    background-color: rgba(46,46,46,1);
    border: 1px solid rgba(143,143,143,1);
    border-radius: 0px;

    -webkit-box-shadow: 0px 0px 3px 1px rgba(0,0,0,1) ;
    -moz-box-shadow: 0px 0px 3px 1px rgba(0,0,0,1) ;
    -ms-box-shadow: 0px 0px 3px 1px rgba(0,0,0,1) ;
    -o-box-shadow: 0px 0px 3px 1px rgba(0,0,0,1) ;
    box-shadow: 0px 0px 3px 1px rgba(0,0,0,1) ;

    -webkit-text-shadow:  1px 1px 2px rgba(0,0,0,1);
    -moz-text-shadow:  1px 1px 2px rgba(0,0,0,1);
    -ms-text-shadow:  1px 1px 2px rgba(0,0,0,1);
    -o-text-shadow:  1px 1px 2px rgba(0,0,0,1);
    text-shadow:  1px 1px 2px rgba(0,0,0,1);

    color:  rgba(255,255,255,0.9);
    text-decoration: none;
    text-transform: none;
}

.creative-gallery-container .creative-gallery-tag.selected {
    background-color: rgba(46,46,46,1);
    border: 1px solid rgba(143,143,143,1);
    border-radius: 0px;

    -webkit-box-shadow: 0px 0px 3px 1px rgba(0,0,0,1) ;
    -moz-box-shadow: 0px 0px 3px 1px rgba(0,0,0,1) ;
    -ms-box-shadow: 0px 0px 3px 1px rgba(0,0,0,1) ;
    -o-box-shadow: 0px 0px 3px 1px rgba(0,0,0,1) ;
    box-shadow: 0px 0px 3px 1px rgba(0,0,0,1) ;

    -webkit-text-shadow:  1px 1px 2px rgba(0,0,0,1);
    -moz-text-shadow:  1px 1px 2px rgba(0,0,0,1);
    -ms-text-shadow:  1px 1px 2px rgba(0,0,0,1);
    -o-text-shadow:  1px 1px 2px rgba(0,0,0,1);
    text-shadow:  1px 1px 2px rgba(0,0,0,1);

    color:  rgba(255,255,255,0.9);
    text-decoration: none;
    text-transform: none;
}
