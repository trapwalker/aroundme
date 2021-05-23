from aiohttp import web
from aioalice import Dispatcher, get_new_configured_app, types
from aioalice.utils.helper import Helper, HelperMode, Item
from aioalice.dispatcher import MemoryStorage
from aioalice.types import Button
from places import POINTS

import datetime
import random


def one_from(*items):
    # TODO: weights support
    variants = []
    for item in items:
        item, cnt = item if isinstance(item, tuple) else (item, 1)
        variants.extend([item] * cnt)
    return random.choice(variants)


def shuffle(*items):
    items = list(items)
    random.shuffle(items)
    return items


def get_context(session: types.Session):
    return contexts.setdefault(session.base.user_id, {})


WEBHOOK_URL_PATH = '/alice/'  # webhook endpoint

WEBAPP_HOST = 'localhost'
WEBAPP_PORT = 8000

dp = Dispatcher(storage=MemoryStorage())


CANCEL_TEXTS = ['отмени', 'прекрати', 'выйти', 'выход', 'хватит', 'перестань', 'заканчивай', 'кончай', 'баста',
                'закройся', 'выключись', 'выключайся', 'завершай']


def DETAILS(c: dict):
    return ' '.join([
        f"Могу {one_from('о чем-то', 'обо всём')} рассказать подробнее, ",
        one_from(
            f"перечислить больше {one_from('мест и событий', 'событий и мест')} {one_from('рядом', 'поблизости', '')}.",
            f"предложить другие {one_from('места и события', 'события и места')} {one_from('рядом', 'поблизости', '')}."
        )
    ])


contexts = {}

state = None


class States(Helper):
    mode = HelperMode.snake_case
    INIT = Item()
    AROUND = Item()  # = select_game
    AROUND_MORE = Item()  # = select_game
    ROUTE = Item()  # = guess_num
    AHEAD = Item()


########################################################################################################################


@dp.request_handler(contains=CANCEL_TEXTS)
async def exit_operation(alice_request):
    user_id = alice_request.session.user_id
    await dp.storage.reset_state(user_id)
    return alice_request.response(
        (
            f'Хорошо! '
            f'{one_from("Если понадоблюсь", "Буду нужна -- ")}, {one_from("я рядом", "позовите", "только позовите")}!.'
            f'{one_from(("Пока!", 2), ("", 4), "Орривидерчи!", "Аста-ла-виста")}'
        ),
        end_session=True,
    )


# @dp.request_handler(state=States.INIT, contains=['вокруг', 'рядом'])
# async def handle_around(r: types.AliceRequest):
#     user_id = r.session.user_id
#     await dp.storage.set_state(user_id, States.AROUND)
#     res =  r.response(
#         ' '.join(
#             shuffle(
#                 f"Вокруг вас много кафе. ",
#                 f"Есть развлечения для детей и взрослых. ",
#                 # f"Кинотеатр Октябрь. ",
#                 f"Много памятников. ",
#                 f"Прокат самокатов. ",
#             ),
#         ) + DETAILS(locals()),
#     )
#     print('around', res)
#     return res


# @dp.request_handler(state=States.AROUND, contains=['ещё', 'больше'])
# async def handle_around_more(r: types.AliceRequest):
#     user_id = r.session.user_id
#     await dp.storage.set_state(user_id, States.AROUND_MORE)
#     res = r.response(
#         ' '.join(
#             shuffle(
#                 f"Рядом с вами Оранжевый остров. ",
#                 f"Памятник Карлу Марксу и Энгельсу. ",
#                 f"Центр Октябрь. ",
#                 f"Парк Аттракционов. ",
#                 f"Общественный Туалет. ",
#             ),
#         ) + DETAILS(locals()),
#     )
#     print('around_more', res)
#     return res


# @dp.request_handler(state=States.AROUND_MORE, contains=['ещё', 'больше'])
# async def handle_around_more_more(r: types.AliceRequest):
#     user_id = r.session.user_id
#     await dp.storage.set_state(user_id, States.AROUND_MORE)
#     return r.response(
#         ' '.join(
#             shuffle(
#                 f"Рядом с вами Оранжевый остров. ",
#                 f"Памятник Карлу Марксу и Энгельсу. ",
#                 f"Центр Октябрь. ",
#                 f"Парк Аттракционов. ",
#                 f"Общественный Туалет. ",
#                 f"Вокруг вас много кафе. ",
#                 f"Есть развлечения для детей и взрослых. ",
#             ),
#         ) + DETAILS(locals()),
#     )


@dp.request_handler(state=States.INIT, contains=['впереди', 'маршрут'])
async def handle_ahead(r: types.AliceRequest):
    user_id = r.session.user_id
    await dp.storage.set_state(user_id, States.AHEAD)
    return r.response(
        (
            f"На вашем пути много интересного. "
        ) + DETAILS(locals()),
    )


INTRO1 = lambda c: (
    f"Привет! Я {one_from('могу рассказать', 'расскажу')}{one_from(' вам', '')} "
    f"о том, что интересного есть рядом с вами "
    f'или впереди по маршруту. '
    f'Просто скажите - "рядом" '
    f'или - "вперед+и.".'
)


@dp.request_handler()
async def handle_all_requests(r: types.AliceRequest):
    global state
    c = get_context(r.session)
    user_id = r.session.user_id
    print(
        f"user>\n"
        f"  {r.request}\n"
        f"  type={r.request.type}\n"
        f"  session={r.session}\n"
        f"  {c}\n"
    )
    if 'запусти навык' in r.request.command or not r.request.command:
        state = 'INIT'
        # await dp.storage.set_state(user_id, States.INIT)
        return r.response(INTRO1(locals()))

    if state == 'INIT':
        state = 'AROUND'
        return r.response(
            ' '.join(
                shuffle(
                    f"Вокруг вас много кафе. ",
                    f"Есть развлечения для детей и взрослых. ",
                    # f"Кинотеатр Октябрь. ",
                    f"Много памятников. ",
                    f"Прокат самокатов. ",
                ),
            ) + DETAILS(locals()),
        )

    if state == 'AROUND':
        state = 'AROUND_MORE'
        return r.response(
            ' '.join(
                shuffle(
                    f"Рядом с вами Оранжевый остров. ",
                    f"Памятник Карлу Марксу и Энгельсу. ",
                    f"Центр Октябрь. ",
                    f"Парк Аттракционов. ",
                    f"Общественный Туалет. ",
                ),
            ) + DETAILS(locals()),
        )

    if state == 'AROUND_MORE':
        state = 'AROUND_MORE_MORE'
        return r.response('Рядом с вами: ' +
            ' '.join(
                shuffle(
                    f"Городской дворец культуры. ",
                    f"Памятник Жертвам Чернобыля. ",
                    f"Кафе Али-Баба. ",
                    f"Собор Николая Чудотворца Иосафа. ",
                    f"Ролледром. ",
                ),
            ) + DETAILS(locals())
        )

    return r.response(f'sil <[200]> +оппа. что значит: {r.request.command}')


@dp.errors_handler()
async def the_only_errors_handler(alice_request, e):
    print(f'ERROR! {e}')
    return alice_request.response(f'Случилось что-то непонятное. Постараюсь больше так не делать.')


if __name__ == '__main__':
    app = get_new_configured_app(dispatcher=dp, path=WEBHOOK_URL_PATH)
    web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)
