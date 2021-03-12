# Steam-game-recommender

## 스팀 게임 추천 시스템(http://www.sgrecommender.kro.kr/)

> 입력받은 게임 목록에 기반해 스팀의 게임을 추천해주는 추천 시스템

### 기술
- 사용 언어: Python, Html, Css, Js
- 백엔드: Flask, pymysql, MariaDB
- 프론트: Jquery

### 추천 시스템
입력받은 게임 목록을 CBF, CF에 기반해 추천 리스트 반환
- CBF: 수집된 모든 유저들이 플레이한 게임의 리스트를 FP-Growth, Word2Vec에 학습시킨 후 입력받은 정보와 유사한 사용자들이 플레이한 다른 게임들을 추천
- CF: 입력한 게임들의 태그의 코사인 유사도를 비교한 후 게임을 추천

### 화면
- 입력 화면
  ![image](https://user-images.githubusercontent.com/34413031/110933187-c84c8a80-836f-11eb-84ac-dedab4a19e21.png)
- 협업 필터링 결과 화면
  ![image](https://user-images.githubusercontent.com/34413031/110933216-d1d5f280-836f-11eb-886a-c5c55ec8494e.png)

- 콘텐츠기반 필터링 결과 화면
  ![image](https://user-images.githubusercontent.com/34413031/110933236-d8fd0080-836f-11eb-928f-36b1ecaaf7b4.png)


웹 페이지 템플릿은 무료 템플릿을 수정해서 사용(https://html5up.net/phantom)
               


