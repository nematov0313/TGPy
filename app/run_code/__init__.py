from telethon.errors import MessageIdInvalidError
from telethon.tl.custom import Message

from app import client
from app import message_design
from app.run_code.meval import meval
from app.run_code.utils import Output, convert_result, filename_prefix, format_traceback
from app.run_code.variables import variables


async def eval_message(code: str, message: Message, uses_orig=False) -> None:
    await message_design.edit_message(message, code, 'Running...')

    output = Output()

    variables['ctx'].msg = message

    kwargs = {}
    if uses_orig:
        orig = await message.get_reply_message()
        kwargs['orig'] = orig

    # noinspection PyBroadException
    try:
        new_variables, result = await meval(
            code,
            f'{filename_prefix}message/{message.chat_id}/{message.id}',
            globals(),
            variables,
            client=client,
            msg=message,
            ctx=variables['ctx'],
            print=output.print,
            **kwargs,
        )
    except Exception:
        result = 'Error occurred'
        exc = ''.join(format_traceback())
    else:
        variables.update(new_variables)
        result = convert_result(result)
        exc = ''

    try:
        await message_design.edit_message(message, code, result, traceback=exc, output=output.text)
    except MessageIdInvalidError:
        pass


import app.run_code.builtin_functions
