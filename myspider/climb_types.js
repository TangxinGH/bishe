/**
 *用于得到职位的大类，在浏览器执行
 */
(function() {

 Array.from(document.querySelector("#root > div.zp-main.zp-main-container-1 > div.zp-container.zp-main__container > div.zp-jobNavigater.zp-main__jobnav > ol").children).forEach((typelist,i) => {
    //类别分类 type一共九个

    var type = Array.from(document.querySelector("#root > div.zp-main.zp-main-container-1 > div.zp-container.zp-main__container > div.zp-jobNavigater.zp-main__jobnav > ol").children)[i];

    //type标题
    var jobtitle = type.querySelector("div.zp-jobNavigater__pop > div.zp-jobNavigater__pop--container > div.zp-jobNavigater__pop--title").textContent;//标题

    console.log("#" + jobtitle);
    //类型，二级
    var genre_list = type.querySelectorAll("div.zp-jobNavigater__pop--list");
    //职位名称
   Array.from( genre_list).forEach((a_tag_list, j) => {
        //职位
         Array.from(a_tag_list.children).forEach((position,j) =>
                                        {console.log(position.text);})
    });
}

);

})();

// 城市 在html 的script中有
/*
*   "hotCity": [{
                                "code": "530",
                                "pinyin": "beijing",
                                "name": "北京"
                            }, {
                                "code": "538",
                                "pinyin": "shanghai",
                                "name": "上海"
                            }, {
                                "code": "765",
                                "pinyin": "shenzhen",
                                "name": "深圳"
                            }, {
                                "code": "763",
                                "pinyin": "guangzhou",
                                "name": "广州"
                            }, {
                                "code": "531",
                                "pinyin": "tianjin",
                                "name": "天津"
                            }, {
                                "code": "801",
                                "pinyin": "chengdu",
                                "name": "成都"
                            }, {
                                "code": "653",
                                "pinyin": "hangzhou",
                                "name": "杭州"
                            }, {
                                "code": "736",
                                "pinyin": "wuhan",
                                "name": "武汉"
                            }, {
                                "code": "600",
                                "pinyin": "dalian",
                                "name": "大连"
                            }, {
                                "code": "613",
                                "pinyin": "changchun",
                                "name": "长春"
                            }, {
                                "code": "635",
                                "pinyin": "nanjing",
                                "name": "南京"
                            }, {
                                "code": "702",
                                "pinyin": "jinan",
                                "name": "济南"
                            }, {
                                "code": "703",
                                "pinyin": "qingdao",
                                "name": "青岛"
                            }, {
                                "code": "639",
                                "pinyin": "suzhou",
                                "name": "苏州"
                            }, {
                                "code": "599",
                                "pinyin": "shenyang",
                                "name": "沈阳"
                            }, {
                                "code": "854",
                                "pinyin": "xian",
                                "name": "西安"
                            }, {
                                "code": "719",
                                "pinyin": "zhengzhou",
                                "name": "郑州"
                            }, {
                                "code": "749",
                                "pinyin": "changsha",
                                "name": "长沙"
                            }, {
                                "code": "551",
                                "pinyin": "chongqing",
                                "name": "重庆"
                            }, {
                                "code": "622",
                                "pinyin": "haerbin",
                                "name": "哈尔滨"
                            }, {
                                "code": "636",
                                "pinyin": "wuxi",
                                "name": "无锡"
                            }, {
                                "code": "654",
                                "pinyin": "ningbo",
                                "name": "宁波"
                            }, {
                                "code": "681",
                                "pinyin": "fuzhou",
                                "name": "福州"
                            }, {
                                "code": "682",
                                "pinyin": "xiamen",
                                "name": "厦门"
                            }, {
                                "code": "565",
                                "pinyin": "shijiazhuang",
                                "name": "石家庄"
                            }, {
                                "code": "664",
                                "pinyin": "hefei",
                                "name": "合肥"
                            }, {
                                "code": "773",
                                "pinyin": "huizhou",
                                "name": "惠州"
                            }, {
                                "code": "576",
                                "pinyin": "taiyuan",
                                "name": "太原"
                            }, {
                                "code": "691",
                                "pinyin": "nanchang",
                                "name": "南昌"
                            }, {
                                "code": "831",
                                "pinyin": "kunming",
                                "name": "昆明"
                            }],
* */