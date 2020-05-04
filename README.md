# Steam-game-recommender

스팀 게임 추천 시스템(http://www.sgrecommender.kro.kr/)

입력받은 게임 목록에 기반해 스팀의 게임을 추천해주는 추천 시스템

run.py
flask를 통해 웹 프론트 ui 제공

recommender.py
입력받은 게임 목록을 CBF, CF에 기반해 추천 리스트 반환
CBF: 수집된 모든 유저들이 플레이한 게임의 리스트를 FP-Growth, Word2Vec에 학습시킨 후 입력받은 정보와 유사한 사용자들이 플레이한 다른 게임들을 추천
CF: 입력한 게임들의 태그와 유사한 태그를 지닌 게임들을 추천

MyModule: 필요한 모듈을을 저장한 디렉토리

웹 페이지 템플릿은 무료 템플릿을 수정해서 사용(https://html5up.net/phantom)
               


